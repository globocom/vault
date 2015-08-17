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
    'actionlogger',
    'dashboard',
    'identity',
    'swiftbrowser',
    'vault',

    'backstage_accounts',
    'allaccess',

    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

BACKSTAGE_ACCOUNTS_URL = os.getenv('VAULT_BACKSTAGE_ACCOUNTS_URL', 'https://accounts.backstage.dev.globoi.com')
BACKSTAGE_BAR_URL = os.getenv('VAULT_BACKSTAGE_BAR_URL', 'https://barra.backstage.dev.globoi.com')
BACKSTAGE_CLIENT_ID = os.getenv('VAULT_BACKSTAGE_CLIENT_ID', 'WUPshuyoPIfjoEn5BsmrUQ==')
BACKSTAGE_CLIENT_SECRET = os.getenv('VAULT_BACKSTAGE_CLIENT_SECRET', 'duMbvbCu9zlvFlvGnhGxMw==')

AUTHENTICATION_BACKENDS = (
    'backstage_accounts.backends.BackstageBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
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

LOGIN_URL = '/admin/vault/login/backstage/'
LOGOUT_URL = '{}/logout'.format(BACKSTAGE_ACCOUNTS_URL)
LOGIN_REDIRECT_URL = '/'

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

# Dashboard
DASHBOARD_WIDGETS = (
    'identity.widgets.ProjectsWidget',
    'dashboard.widgets.BaseWidget',
)

# Keystone
KEYSTONE_URL = os.getenv('VAULT_KEYSTONE_URL', 'https://auth.s3.dev.globoi.com:5000/v2.0')
KEYSTONE_VERSION = 2

# When versioning is enabled in a container named <container>, another
# container named <prefix><container> will be create to keep objects versions
SWIFT_VERSION_PREFIX = os.getenv('VAULT_SWIFT_VERSION_PREFIX', '_version_')

# True if you are using invalid SSL certs
if os.environ.get('VAULT_SWIFT_INSECURE') == 'False':
    SWIFT_INSECURE = False
else:
    SWIFT_INSECURE = True

USERNAME_BOLADAO = os.getenv('USERNAME_BOLADAO', 'storm')
PASSWORD_BOLADAO = os.getenv('PASSWORD_BOLADAO', 'storm')
PROJECT_BOLADAO = os.getenv('PROJECT_BOLADAO', 'infra')
# ID da role swiftoperator
ROLE_BOLADONA = os.getenv('ROLE_BOLADONA', 'c573d07d11ed4f75a7cae8e7527eb1ed')
