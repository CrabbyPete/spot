# Django settings for spot project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Pete Douma', 'pete.douma@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME'    : 'douma_spot',               # Or path to database file if using sqlite3.
        'USER'    : 'douma_spot',               # Not used with sqlite3.
        'PASSWORD': 'flyr0d',                   # Not used with sqlite3.
        'HOST'    : '',                         # Set to empty string for localhost. Not used with sqlite3.
        'PORT'    : '',                         # Set to empty string for default. Not used with sqlite3.
        
        'STORAGE_ENGINE': 'MyISAM'              # Default storage engine for South
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

DEFAULT_FROM_EMAIL  = 'fish@spotburn.com'
JOIN_BY_PHONE_EMAIL = 'fish@spotburn.com'
JOIN_BY_EMAIL       = 'join@spotburn.com'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

import os.path
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "site_media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/'



# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9t8fpqi0=aqbj93^&*_0mth46coq=s#b*wbhah^5uvu-jmnq5y'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# Added to get the current URL
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.auth',
)

MIDDLEWARE_CLASSES = ( 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

FACEBOOK_API_KEY = 'c7a63e78e191d89e6debd31ee262ae64' 
FACEBOOK_SECRET_KEY = '4f7d981014f7fc073f7a6263352fa479' 
FACEBOOK_INTERNAL = True
FACEBOOK_APP_NAME ="Spotburn"


ROOT_URLCONF = 'spot.urls'
AUTH_PROFILE_MODULE = 'base.SpotUser'

# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.comments',
    'notification',
	'base',
    'friends',
    'imagekit',
)


SITE_ID = 1
SITE_NAME = 'localhost:8000'
SITE_BASE = 'http://'+SITE_NAME
LOGIN_URL = SITE_BASE

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


