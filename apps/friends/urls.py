from django.conf.urls.defaults import *

from  friends import views

urlpatterns = patterns('',
    # Search for friends
    url(r'^search/$','friends.views.search', name='friends_search'),

    # Show a friends page
    url(r'^show/$','friends.views.show', name='friends_show'),

    # Invite a friend
    url(r'^invite/$','friends.views.invite', name='friends_invite'),

    # Invite a contact
    url(r'^contact/$','friends.views.contact', name='friends_contact'),

    # Add a friend
    url(r'^add/$', 'friends.views.add', name='friends_add'),

    # Dump a friend
    url(r'^dump/$', 'friends.views.dump', name='friends_dump'),

    # Follow (and unfollow) a friend
    url(r'^dump/$', 'friends.views.follow', name='friends_follow'),
)
