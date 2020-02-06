# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SwiftBrowserConfig(AppConfig):
    name = 'swiftbrowser'
    verbose_name = _("Swift Browser")
    info_endpoint = '/storage/info'
