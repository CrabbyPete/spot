from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 			'base.views.homepage', name='homepage'),
    (r'^base/',         include('base.urls')  	       ),
    (r'^about/',        include('about.urls') 	       ),
	(r'^friends/',      include('friends.urls')        ),
	(r'^notification/', include('notification.urls')   ),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')   ),
    url(r'^admin/',     include(admin.site.urls)                   ),
)


import os
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(os.path.dirname(__file__), "site_media")}),
   )

