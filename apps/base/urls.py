from django.conf.urls.defaults import *

from base import views, models
from base.forms import *


urlpatterns = patterns('',

    # default index
    url(r'^$', 'base.views.homepage', name='base_index'),
    
    # base view my page
    url(r'mypage/$', 'base.views.my_page', name='base_my_page'),

    # base view user and friends messages
    url(r'^viewall/$', 'base.views.view_all', name='base_view_all'),

    # base message page
    url(r'^message/$', 'base.views.message', name='base_message'),

    # base message delete
    url(r'^messagedelete/$', 'base.views.message_delete', name='base_message_delete'),

    url(r'^nextmessage/$', 'base.views.next_messages', name='base_next_messages'),

    url(r'^prevmessage/$', 'base.views.prev_messages', name='base_prev_messages'),

    # add and delete a comment to a post
    url(r'^commentadd/$',   'base.views.add_comment',      name='base_add_comment'),
    url(r'^commentdelete/$','base.views.delete_comment',   name='base_delete_comment'),
    url(r'^commentmap/$',   'base.views.map_comment',      name='base_popup_map'),
    

    # base login page: this is the start page for sign up and sign in forms
    url(r'^login/$', 'base.views.login', name='base_login'),

    # base signup page
    url(r'^signup/$', 'base.views.signup', name='base_signup'),

    # base signin page
    url(r'^signin/$', 'base.views.signin', name='base_signin'),

    # base logout: sets up a blank sign in sheet
    url(r'^logout/$', 'base.views.goodbye', name='base_logout'),

    # base editprofile: sets up a blank sign in sheet
    url(r'^editprofile/$', 'base.views.editprofile', name='base_editprofile'),

    # base get a friends page
    url(r'^showgroup/$', 'base.views.showgroup', name='base_showgroup'),

    # base create/edit a group
    url(r'^group/$', 'base.views.editgroup', name='base_group'),
    
    # base add a new post
    url(r'^addpost/$', 'base.views.add_post', name='base_addpost'),

    # base ajax : Changes the picture on the index page
    url(r'^ajax/$', 'base.views.ajax', name='base_ajax'),

    # base ajaxradio : for radio buttons on user follow form
    url(r'^ajaxradio/$', 'base.views.ajaxradio', name='base_ajaxradio'),

   # base my page
   #url(r'^mypage/$', 'base.views.mypage', name='base_mypage'),
)
