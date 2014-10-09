# -*- coding:utf-8 -*-

from vault.settings.base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': PROJECT,
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'HOST': os.getenv('MYSQL_HOST'),
        'PORT': os.getenv('MYSQL_PORT'),
    }
}

STATIC_URL = os.getenv('VAULT_STATIC_URL')

# Keystone
OPENSTACK_API_VERSIONS = {
    "identity": 2
}

KEYSTONE_VERSION = OPENSTACK_API_VERSIONS.get('identity', 2)

if KEYSTONE_VERSION == 3:
    OPENSTACK_KEYSTONE_URL = "%s/v3" % os.getenv('VAULT_KEYSTONE_URL')
else:
    OPENSTACK_KEYSTONE_URL = "%s/v2.0" % os.getenv('VAULT_KEYSTONE_URL')
