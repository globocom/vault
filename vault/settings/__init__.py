# -*- coding:utf-8 -*-

"""
Django settings for vault project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import importlib
import os


def get_settings_path():
    """
    Retrieve settings path according to value set in the
    environment variable ENVIRON.

    If ENVIRON is not defined, use 'local' as default.
    """
    environ_name = os.getenv('ENVIRON', 'local').lower()
    return "vault.settings.{}".format(environ_name)


def load_module_attributes(settings_path):
    """
    Provided the module path, copy given module attributes
    to this module.
    """
    module = importlib.import_module(settings_path)
    attrlist = dir(module)

    for attr in attrlist:
        globals()[attr] = getattr(module, attr)


settings_path = get_settings_path()
print("Using settings from '{}'".format(settings_path))
load_module_attributes(settings_path)
