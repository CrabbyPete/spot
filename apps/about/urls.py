from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^$',         direct_to_template, {"template": "about/about.html"},           name="about"),
    url(r'^terms/$',   direct_to_template, {"template": "about/terms_of_use.html"},    name="terms"),
    url(r'^privacy/$', direct_to_template, {"template": "about/privacy_policy.html"},  name="privacy"),
    url(r'^contact/$', 'about.views.contact_us',                                       name="contact_us"),
)
