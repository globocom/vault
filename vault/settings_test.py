# -*- coding: utf-8 -*-

from .settings import *


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASES_DEFAULT_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DATABASES_DEFAULT_NAME', 'vault_test.db'),
    }
}
