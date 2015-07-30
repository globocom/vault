# -*- coding:utf-8 -*-

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
urllib3.disable_warnings()

PROJECT = 'vault'

DEBUG = False if os.environ.get('VAULT_DEBUG') == 'False' else True

TEMPLATE_DEBUG = DEBUG

SECRET_KEY = 'l^9r^^ksywons-@!(o+02k-)@o$ko3hw7(w6d=*tu=(b_yy%p0'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = (
    # 'backstage_accounts',
    # 'allaccess',

    # 'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'openstack_auth',
    'dashboard',
    'identity',
    'swiftbrowser',
    'vault',
)

# BACKSTAGE_ACCOUNTS_URL = os.getenv('VAULT_BACKSTAGE_ACCOUNTS_URL', 'https://accounts.backstage.dev.globoi.com'),
# BACKSTAGE_BAR_URL = os.getenv('VAULT_BACKSTAGE_BAR_URL', 'https://barra.backstage.dev.globoi.com'),
# BACKSTAGE_CLIENT_ID = os.getenv('VAULT_BACKSTAGE_CLIENT_ID', 'Zmru7+GPPMSAeHFYOKsVyg=='),
# BACKSTAGE_CLIENT_SECRET = os.getenv('VAULT_BACKSTAGE_CLIENT_SECRET', '40Xu96XwLCNnQRSubJFwEA=='),

BACKSTAGE_ACCOUNTS_URL = "https://accounts.backstage.dev.globoi.com"
BACKSTAGE_BAR_URL = "https://barra.backstage.dev.globoi.com"
BACKSTAGE_CLIENT_ID = 'WUPshuyoPIfjoEn5BsmrUQ==',
BACKSTAGE_CLIENT_SECRET = 'duMbvbCu9zlvFlvGnhGxMw==',

AUTHENTICATION_BACKENDS = (
    # 'backstage_accounts.backends.BackstageBackend',
    # 'openstack_auth.backend.KeystoneBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'vault.urls'

WSGI_APPLICATION = 'vault.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = 'vault_static/'

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)


STATIC_URL = '{}/{}'.format(os.getenv('SWIFT_PUBLIC_URL', ''), STATIC_ROOT)

# Keystone
OPENSTACK_SSL_NO_VERIFY = True

# LOGIN_URL = '/auth/login/'
# LOGOUT_URL = '/auth/logout'
# LOGIN_REDIRECT_URL = '/'

# The openstack_auth.user.Token object isn't JSON-serializable ATM
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# ENV Confs

PAGINATION_SIZE = os.getenv('VAULT_PAGINATION_SIZE', 50)

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

# Keystone
OPENSTACK_API_VERSIONS = {
    "identity": 2
}

if os.environ.get('VAULT_KEYSTONE_CREATE_USER') == 'False':
    KEYSTONE_CREATE_USER = False
else:
    KEYSTONE_CREATE_USER = True

KEYSTONE_VERSION = OPENSTACK_API_VERSIONS.get('identity', 2)

if KEYSTONE_VERSION == 3:
    OPENSTACK_KEYSTONE_URL = "%s/v3" % os.getenv('VAULT_KEYSTONE_URL')
else:
    OPENSTACK_KEYSTONE_URL = "%s/v2.0" % os.getenv('VAULT_KEYSTONE_URL')

# When versioning is enabled in a container named <container>, another
# container named <prefix><container> will be create to keep objects versions
SWIFT_VERSION_PREFIX = os.getenv('VAULT_SWIFT_VERSION_PREFIX', '_version_')

# True if you are using invalid SSL certs
if os.environ.get('VAULT_SWIFT_INSECURE') == 'False':
    SWIFT_INSECURE = False
else:
    SWIFT_INSECURE = True
