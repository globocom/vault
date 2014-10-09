# -*- coding:utf-8 -*-

from vault.settings.base import *


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': PROJECT,
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'SUPPORTS_TRANSACTIONS': False,
    }
}

STATIC_URL = '/static/'

# Keystone
OPENSTACK_API_VERSIONS = {
    "identity": 2
}

KEYSTONE_VERSION = OPENSTACK_API_VERSIONS.get('identity', 2)

if KEYSTONE_VERSION == 3:
    OPENSTACK_KEYSTONE_URL = "%s/v3" % os.getenv('VAULT_KEYSTONE_URL')
else:
    OPENSTACK_KEYSTONE_URL = "%s/v2.0" % os.getenv('VAULT_KEYSTONE_URL')

SWIFT_INSECURE = True
