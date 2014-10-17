# -*- coding:utf-8 -*-

"""
Django settings for vault project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os


PROJECT = 'vault'

SECRET_KEY = 'l^9r^^ksywons-@!(o+02k-)@o$ko3hw7(w6d=*tu=(b_yy%p0'

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'openstack_auth',

    'vault',
    'dashboard',
    'identity',
    'swiftbrowser',
)

try:
    if DEBUG:
        INSTALED_APPS = INSTALED_APPS + (
            'jstest'
        )
except:
    pass

AUTHENTICATION_BACKENDS = (
    'openstack_auth.backend.KeystoneBackend',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

ROOT_URLCONF = 'vault.urls'

WSGI_APPLICATION = 'vault.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_ROOT = 'statictemp/'

STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

# Keystone
OPENSTACK_SSL_NO_VERIFY = True

LOGIN_URL = '/auth/login/'
LOGOUT_URL = '/auth/logout'
LOGIN_REDIRECT_URL = '/'

# The openstack_auth.user.Token object isn't JSON-serializable ATM
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


# ENV Confs

DEBUG = os.getenv('VAULT_DEBUG', True)
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': PROJECT,
        'USER': os.getenv('VAULT_MYSQL_USER', 'root'),
        'PASSWORD': os.getenv('VAULT_MYSQL_PASSWORD', ''),
        'HOST': os.getenv('VAULT_MYSQL_HOST', ''),
        'PORT': os.getenv('VAULT_MYSQL_PORT', 3306),
    }
}

STATIC_URL = os.getenv('VAULT_STATIC_URL', '/static/')

# Keystone
OPENSTACK_API_VERSIONS = {
    "identity": 2
}

KEYSTONE_VERSION = OPENSTACK_API_VERSIONS.get('identity', 2)

if KEYSTONE_VERSION == 3:
    OPENSTACK_KEYSTONE_URL = "%s/v3" % os.getenv('VAULT_KEYSTONE_URL')
else:
    OPENSTACK_KEYSTONE_URL = "%s/v2.0" % os.getenv('VAULT_KEYSTONE_URL')

SWIFT_INSECURE = os.getenv('VAULT_SWIFT_INSECURE', True)
