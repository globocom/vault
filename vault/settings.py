# -*- coding: utf-8 -*-
"""
Django settings for vault project.
"""

import os
import importlib
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("VAULT_SECRET_KEY", "vaultsecretkey")

PROJECT = "vault"

DEBUG = False if os.environ.get("VAULT_DEBUG") == "False" else True

ALLOWED_HOSTS = ["*"]

# Disable HTTPS verification warnings in debug mode
if DEBUG:
    from requests.packages import urllib3
    urllib3.disable_warnings()

ENVIRON = os.getenv("VAULT_ENVIRON", None)

INSTALLED_APPS = [
    "allaccess",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "vault",
    "actionlogger",
    "storage",
    "identity",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allaccess.backends.AuthorizedServiceBackend",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "vault.context_processors.vault_settings",
                "vault.context_processors.vault_session",
            ],
        },
    },
]

WSGI_APPLICATION = "vault.wsgi.application"

ROOT_URLCONF = "vault.urls"

LOGIN_URL = "/admin/login/"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

# Internationalization
LANGUAGE_CODE = os.getenv("VAULT_LANGUAGE", "en-us")
LANGUAGES = (
    ("en", _("English")),
    ("pt-BR", _("Portuguese")),
)

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = "vault_static/"

STATIC_URL = "{}/{}/{}".format(os.getenv("SWIFT_INTERNAL_URL", ""),
                               os.getenv("SWIFT_CONTAINER", "vault"),
                               STATIC_ROOT)

# The openstack_auth.user.Token object isn't JSON-serializable ATM
SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

PAGINATION_SIZE = os.getenv("VAULT_PAGINATION_SIZE", 50)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("VAULT_MYSQL_DB", PROJECT),
        "USER": os.getenv("VAULT_MYSQL_USER", "root"),
        "PASSWORD": os.getenv("VAULT_MYSQL_PASSWORD", ""),
        "HOST": os.getenv("VAULT_MYSQL_HOST", "127.0.0.1"),
        "PORT": int(os.getenv("VAULT_MYSQL_PORT", 3306)),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

MAX_FILES_UPLOAD = os.getenv("MAX_FILES_UPLOAD", 10)

# Help url
HELP_URL = os.getenv("VAULT_HELP_URL")

# Proxy
VAULT_HTTPS_PROXY = os.getenv("VAULT_HTTPS_PROXY")
VAULT_HTTP_PROXY = os.getenv("VAULT_HTTP_PROXY")

# When versioning is enabled in a container named <container>, another
# container named <prefix><container> will be created to keep objects versions
SWIFT_VERSION_PREFIX = os.getenv("VAULT_SWIFT_VERSION_PREFIX", "_version_")
SWIFT_TRASH_PREFIX = ".trash"
SWIFT_HIDE_PREFIXES = [SWIFT_VERSION_PREFIX, SWIFT_TRASH_PREFIX]

# Backup
BACKUP_ENABLED = False
if os.getenv("VAULT_BACKUP_ENABLED") == "True":
    BACKUP_ENABLED = True
BACKUP_USER = os.getenv("VAULT_BACKUP_USER")
BACKUP_USER_ROLE = os.getenv("VAULT_BACKUP_USER_ROLE")
BACKUP_API_URL = os.getenv("VAULT_BACKUP_API_URL")
BACKUP_API_USER = os.getenv("VAULT_BACKUP_API_USER")
BACKUP_API_PASSWORD = os.getenv("VAULT_BACKUP_API_PASSWORD")
BACKUP_OBJECT_COUNT_VALUE = os.getenv("BACKUP_OBJECT_COUNT_VALUE", "10000")
BACKUP_OBJECT_BYTES_VALUE = os.getenv("BACKUP_OBJECT_BYTES_VALUE",
                                      "1000000000")

# True if you are using invalid SSL certs
SWIFT_INSECURE = False
if os.environ.get("VAULT_SWIFT_INSECURE") == "True":
    SWIFT_INSECURE = True

# Timeout for requests made with swiftclient
SWIFT_REQUESTS_TIMEOUT = os.getenv("VAULT_SWIFT_REQUESTS_TIMEOUT", 60)

# Keystone
KEYSTONE_USERNAME = os.getenv("VAULT_KEYSTONE_USERNAME", "u_vault")
KEYSTONE_PASSWORD = os.getenv("VAULT_KEYSTONE_PASSWORD", "u_vault")
KEYSTONE_PROJECT = os.getenv("VAULT_KEYSTONE_PROJECT", "Vault")
KEYSTONE_VERSION = os.getenv("VAULT_KEYSTONE_API_VERSION", 3)
KEYSTONE_URL = os.getenv(
    "VAULT_KEYSTONE_URL", "http://localhost:5000/{}".format(
        "v2.0" if KEYSTONE_VERSION == 2 else "v3"))

KEYSTONE_TIMEOUT = os.getenv("VAULT_KEYSTONE_TIMEOUT", 3)
# KEYSTONE_INSECURE = False
KEYSTONE_ROLE = os.getenv("VAULT_KEYSTONE_ROLE")  # swiftoperator role ID

# Cache cleanning API
CACHESWEEP_API = os.getenv("CACHESWEEP_API", "http://localhost/")

IDENTITY_SECRET_KEY = os.getenv("IDENTITY_SECRET_KEY")

if not IDENTITY_SECRET_KEY and DEBUG:
    IDENTITY_SECRET_KEY = "SRTAYZDUnNSW9xhBStvylCgmCY5jo3zedqDNbdRN3Ek="

# Swift-Cloud
SWIFT_CLOUD_ENABLED = False
if os.getenv("VAULT_SWIFT_CLOUD_ENABLED") == "True":
    SWIFT_CLOUD_ENABLED = True

SWIFT_CLOUD_TOOLS_URL = os.getenv(
    "VAULT_SWIFT_CLOUD_TOOLS_URL", "http://localhost:8888/v1")
SWIFT_CLOUD_TOOLS_API_KEY = os.getenv(
    "VAULT_SWIFT_CLOUD_TOOLS_API_KEY", "toolsapikey")

# Logging conf
LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "identity": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "vault": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "storage": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
        "dashboard": {
            "handlers": ["console"],
            "propagate": True,
            "level": "DEBUG",
        },
    },
}


def load_apps_settings():
    """Load Apps' settings"""

    new_settings = {}
    for app in INSTALLED_APPS:
        try:
            module = importlib.import_module(app)
            module_apps = importlib.import_module(app + ".apps")
            app_config = getattr(module_apps,
                                 module.default_app_config.split(".")[-1])
            if app_config.vault_app is True:
                app_settings = importlib.import_module(app + ".settings")
                names = [
                    x for x in app_settings.__dict__ if not x.startswith("_")
                ]
                new_settings.update(
                    {k: getattr(app_settings, k)
                     for k in names})
        # Ignores apps that don't have a "vault_app = True" in their apps.py file
        # or don't have a settings.py file
        except (AttributeError, ModuleNotFoundError) as e:
            pass
    return new_settings


globals().update(load_apps_settings())
