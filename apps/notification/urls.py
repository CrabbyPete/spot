from django.conf.urls.defaults import *

from notification import views


urlpatterns = patterns('',
  # Show notices
    url(r'^index/$', 'notification.views.index', name='notice_index'),
    url(r'^delete/$', 'notification.views.delete', name='notice_delete'),
    url(r'^accept/$', 'notification.views.accept', name='notice_accept'),
)