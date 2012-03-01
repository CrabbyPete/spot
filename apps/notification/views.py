from django.contrib.auth.models import      User
from django.template import                 Context
from django.template.loader import          get_template
from django.http import                     HttpResponse
from django.db.models import                Q

from django.contrib import                  auth
from django.template                import  RequestContext
from django.shortcuts import                render_to_response
from django.views.generic.simple import     direct_to_template


from friends.models import                  *

from notification.models import *

def index(request):
    user = request.user
    profile = user.get_profile()
    notices = Notice.objects.notices_for(user)

    c = Context({'user':user, 'profile':profile, 'notices':notices})
    return render_to_response('notices.html', c, context_instance=RequestContext(request))

# Delete the notice
def delete(request):
    if request.GET:
        n = request.GET["notice"]
        if n != '':
            notice = Notice.objects.get(pk=n)
            notice.delete()
    return index(request)

def accept(request):
    if request.GET:
        n = request.GET["notice"]
        notice = Notice.objects.get(pk=n)
        if notice.notice_type == "friends_invite":
            invite = FriendshipInvitation.objects.get(from_user = notice.sent_by, to_user = notice.user )
            invite.accept()
            notice.delete()
    return index(request)


