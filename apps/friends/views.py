# Friends views
from django.db.models import                Q

from django.template                import  Context
from django.template.loader         import  get_template
from django.template                import  RequestContext
from django.shortcuts               import  render_to_response
from django.views.generic.simple    import  direct_to_template
from django.http                    import  HttpResponse, HttpResponseRedirect


from django.contrib import                  auth
from django.contrib.auth.models import      User

from base.models import                     *
from base.views import                      message_list, next_messages, prev_messages
from friends.models import                  *
from friends.forms import                   *
from notification.models import             *

# Search for users
def search (request):

    # User should be loggin by now
    if request.user.is_authenticated():
        profile = request.user.get_profile()
    else:
        profile = None
        
    results = []
    # Resubmit form
    def submit_form(fform):
        iform = InviteFriendsForm()
        return direct_to_template(request, template='search.html',
                                extra_context={'profile':profile,
                                                'iform':iform,
                                                'fform':fform,
                                                'results':results}  )

    # Was this a POST or the first time we are here
    if not request.POST:
        fform = FindFriendsForm()
        return submit_form(fform)

    # Check for form errors
    fform = FindFriendsForm(request.POST)
    if not fform.is_valid():
        return submit_form(fform)

    # For query's for each field
    find_user = fform.cleaned_data['user']
    locate = fform.cleaned_data['location']
    interest = fform.cleaned_data['interest']

    if find_user != "":
        q_u = User.objects.filter(Q(username__istartswith = find_user))
        for u in q_u:
            results.append(u)

    qry = None
    if locate != "" :
        qry = Q(address__icontains = locate)

    if interest != "":
        if qry == None:
            qry = Q(fish_method__icontains = interest)
        else:
            qry = qry | Q(fish_method__icontains = interest)

    if qry != None:
        qry = SpotUser.objects.filter(qry)
        for result in qry:
            if result in results:
                continue
            else:
                results.append(result.user)

    # Don't show those already friends or yourself
    if request.user.is_anonymous():
        pass
    else:
        for result in reversed(results):
            if Friendship.objects.are_friends(result, request.user) or result == request.user:
                results.remove(result)

    return submit_form(fform)


# Show a friends page
def show(request):
#    if request.user.is_authenticated():
#        profile = request.user.get_profile()
    if request.GET:
        u = request.GET['friend']
        user = User.objects.get(pk=u)
        profile = user.get_profile()
  
        friends = Friendship.objects.friends_for_user(user)
        friend  = Friendship.objects.are_friends(request.user, user)
        
        groups = SpotGroup.objects.groups_for(user)
        m,next,prev = SpotMessage.objects.for_user(user,0,20)
        visit = True;
        
        c = Context({'profile':profile, 
                     'friends':friends,
                     'friend':friend,  
                     'groups':groups, 
                     'messages':m,
                     'visit':True       })
        
        return render_to_response('mypage.html', c, context_instance=RequestContext(request))
    # Should not hit this, but if so,
    else:
        return HttpResponseRedirect('/')

# Invite an existing member to be friends
def invite(request):

    # User should be loggin by now
    if request.user.is_authenticated():
            profile = request.user.get_profile()

    def submit_form():
        results = []
        fform = FindFriendsForm()
        return direct_to_template(request, template='search.html',
                                    extra_context={'profile':profile,
                                    'iform':iform,
                                    'fform':fform,
                                    'results':results}
                                 )

    # Was this a submitted form or the first time here?
    if not request.GET:
        iform = InviteFriendsForm()
        submit_form()

    # This was a POST, check what was submitted
    iform = InviteFriendsForm(request.POST)
    if not iform.is_valid():
        return submit_form()

    u = request.GET['friend']
    user = User.objects.get(pk=u)

    # Invitation sent.
    invite = FriendshipInvitation( from_user = request.user, to_user = user )
    invite.request()
    return HttpResponseRedirect('/')

# Invite a contact who is not a member to join
def contact(request):
    # User should be loggin by now
    if request.user.is_authenticated():
            profile = request.user.get_profile()

    def submit_form():
        results = []
        fform = FindFriendsForm()
        return direct_to_template(request, template='search.html',
                                    extra_context={'profile':profile,
                                    'iform':iform,
                                    'fform':fform,
                                    'results':results}                  )

    # Was this a submitted form or the first time here?
    if not request.POST:
        iform = InviteFriendsForm()
        submit_form()

    # This was a POST, check what was submitted
    iform = InviteFriendsForm(request.POST)
    if not iform.is_valid():
        return submit_form()

    email = iform.cleaned_data['email']
    phone = iform.cleaned_data['phone']
    messg = iform.cleaned_data['message']

    # See if this address is already a member
    try:
        member = User.objects.get(Q(email = email))
    except User.DoesNotExist:
        member = ''
    """ Don't do this now, It exposes phone numbers
    try:
        member = SpotUser.objects.get(Q(mobile=phone))
    except SpotUser.DoesNotExist:
        member = ''
    """
    if member != '':
        return invite(request)

    rfj = JoinInvitation.objects.send_invitation(from_user = request.user, message = messg, to_email = email)
    return HttpResponseRedirect('/')

def add(request):
    if request.POST:
       friends = friend_set_for(request.user)
    return

def dump(request):
    pass

def follow(request):
    pass