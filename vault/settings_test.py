# -*- coding: utf-8 -*-

from settings import *


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASES_DEFAULT_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DATABASES_DEFAULT_NAME', 'vault_test'),
        'USER': os.getenv('DATABASES_DEFAULT_USER', 'root'),
        'PASSWORD': os.getenv('DATABASES_DEFAULT_PASSWORD', ''),
        'HOST': os.getenv('DATABASES_DEFAULT_HOST', ''),
        'PORT': os.getenv('DATABASES_DEFAULT_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
