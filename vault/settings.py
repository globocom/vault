# -*- coding: utf-8 -*-

"""
Django settings for vault project.
"""

import os
from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'mzjhdtd6fpisubo863qi%j%!u=q&p_^ban=+*#xzz*0sel^2lp'

PROJECT = 'vault'

DEBUG = False if os.environ.get('VAULT_DEBUG') == 'False' else True

ALLOWED_HOSTS = ['*']

# Disable HTTPS verification warnings in debug mode
if DEBUG:
    from requests.packages import urllib3
    urllib3.disable_warnings()

ENVIRON = os.getenv('VAULT_ENVIRON', None)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vault',
    'actionlogger',
    'dashboard',
    'identity',
    'swiftbrowser',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allaccess.backends.AuthorizedServiceBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

WSGI_APPLICATION = 'vault.wsgi.application'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

ROOT_URLCONF = 'vault.urls'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-BR.UTF-8'
LANGUAGES = (
    ('pt-BR', _('Portuguese')),
    ('en', _('English')),
)

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = 'vault_static/'

STATIC_URL = '{}/{}/{}'.format(os.getenv('SWIFT_INTERNAL_URL', ''),
                               os.getenv('SWIFT_CONTAINER', 'vault'),
                               STATIC_ROOT)


# The openstack_auth.user.Token object isn't JSON-serializable ATM
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

PAGINATION_SIZE = os.getenv('VAULT_PAGINATION_SIZE', 20)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('VAULT_MYSQL_DB', PROJECT),
        'USER': os.getenv('VAULT_MYSQL_USER', 'root'),
        'PASSWORD': os.getenv('VAULT_MYSQL_PASSWORD', ''),
        'HOST': os.getenv('VAULT_MYSQL_HOST', ''),
        'PORT': int(os.getenv('VAULT_MYSQL_PORT', 3306)),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

MAX_FILES_UPLOAD = os.getenv('MAX_FILES_UPLOAD', 10)

# Proxy
VAULT_HTTPS_PROXY = os.getenv('VAULT_HTTPS_PROXY')
VAULT_HTTP_PROXY = os.getenv('VAULT_HTTP_PROXY')

# When versioning is enabled in a container named <container>, another
# container named <prefix><container> will be created to keep objects versions
SWIFT_VERSION_PREFIX = os.getenv('VAULT_SWIFT_VERSION_PREFIX', '_version_')
SWIFT_TRASH_PREFIX = '.trash'
SWIFT_HIDE_PREFIXES = [SWIFT_VERSION_PREFIX, SWIFT_TRASH_PREFIX]

# Backup
BACKUP_USER = os.getenv('VAULT_BACKUP_USER', 'u_backup')
BACKUP_USER_ROLE = os.getenv('VAULT_BACKUP_USER_ROLE', 'swiftoperator')
BACKUP_API_URL = os.getenv('VAULT_BACKUP_API_URL', 's3backup.dev.globoi.com:5572')
BACKUP_API_USER = os.getenv('VAULT_BACKUP_API_USER')
BACKUP_API_PASSWORD = os.getenv('VAULT_BACKUP_API_PASSWORD')
BACKUP_OBJECT_COUNT_VALUE = os.getenv('BACKUP_OBJECT_COUNT_VALUE', '10000')
BACKUP_OBJECT_BYTES_VALUE = os.getenv('BACKUP_OBJECT_BYTES_VALUE', '1000000000')

# True if you are using invalid SSL certs
if os.environ.get('VAULT_SWIFT_INSECURE') == 'False':
    SWIFT_INSECURE = False
else:
    SWIFT_INSECURE = True

# Keystone
KEYSTONE_USERNAME = os.getenv('VAULT_KEYSTONE_USERNAME')
KEYSTONE_PASSWORD = os.getenv('VAULT_KEYSTONE_PASSWORD')
KEYSTONE_PROJECT = os.getenv('VAULT_KEYSTONE_PROJECT')
KEYSTONE_URL = os.getenv('VAULT_KEYSTONE_URL')
KEYSTONE_VERSION = 3

# swiftoperator role ID
KEYSTONE_ROLE = os.getenv('VAULT_KEYSTONE_ROLE')

# Cache cleanning API
CACHESWEEP_API = os.getenv('CACHESWEEP_API', 'http://localhost/')

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
