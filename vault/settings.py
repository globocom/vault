# -*- coding: utf-8 -*-

"""
Django settings for vault project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os

# Disable HTTPS verification warnings.
from requests.packages import urllib3
from django.utils.translation import ugettext_lazy as _
urllib3.disable_warnings()

PROJECT = 'vault'

DEBUG = False if os.environ.get('VAULT_DEBUG') == 'False' else True

TEMPLATE_DEBUG = DEBUG

SECRET_KEY = 'l^9r^^ksywons-@!(o+02k-)@o$ko3hw7(w6d=*tu=(b_yy%p0'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = (
    'actionlogger',
    'dashboard',
    'identity',
    'swiftbrowser',
    'vault',

    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

ROOT_URLCONF = 'vault.urls'

WSGI_APPLICATION = 'vault.wsgi.application'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'pt-BR.UTF-8'
LANGUAGES = (
    ('pt-BR', _('Portuguese')),
    ('en', _('English')),
)
TIME_ZONE = 'America/Sao_Paulo'

STATIC_ROOT = 'vault_static/'

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

STATIC_URL = '{}/{}'.format(os.getenv('SWIFT_PUBLIC_URL', ''), STATIC_ROOT)

LOGIN_URL = '/login/'
# ENV Confs

PAGINATION_SIZE = os.getenv('VAULT_PAGINATION_SIZE', 10)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('VAULT_MYSQL_DB', PROJECT),
        'USER': os.getenv('VAULT_MYSQL_USER', 'root'),
        'PASSWORD': os.getenv('VAULT_MYSQL_PASSWORD', ''),
        'HOST': os.getenv('VAULT_MYSQL_HOST', ''),
        'PORT': int(os.getenv('VAULT_MYSQL_PORT', 3306)),
    }
}

# Dashboard
DASHBOARD_WIDGETS = (
    'swiftbrowser.widgets.ProjectsWidget',
)


# Keystone
KEYSTONE_URL = os.getenv('VAULT_KEYSTONE_URL', 'https://auth.s3.dev.globoi.com:5000/v2.0')
KEYSTONE_VERSION = 2

KEYSTONE_USERNAME = os.getenv('VAULT_KEYSTONE_USERNAME', 'user')
KEYSTONE_PASSWORD = os.getenv('VAULT_KEYSTONE_PASSWORD', 'pass')
KEYSTONE_PROJECT = os.getenv('VAULT_KEYSTONE_PROJECT', 'project')

# swiftoperator role ID
KEYSTONE_ROLE = os.getenv('VAULT_KEYSTONE_ROLE', 'swiftoperatorroleid')


# When versioning is enabled in a container named <container>, another
# container named <prefix><container> will be created to keep objects versions
SWIFT_VERSION_PREFIX = os.getenv('VAULT_SWIFT_VERSION_PREFIX', '_version_')

SWIFT_HIDE_PREFIXES = [
    '.',
    SWIFT_VERSION_PREFIX
]

# True if you are using invalid SSL certs
if os.environ.get('VAULT_SWIFT_INSECURE') == 'False':
    SWIFT_INSECURE = False
else:
    SWIFT_INSECURE = True

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'identity': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'ERROR',
        },
        'vault': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'ERROR',
        },
        'swiftbrowser': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'ERROR',
        },
        'dashboard': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'ERROR',
        }
    },
}
