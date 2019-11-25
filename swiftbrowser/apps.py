# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SwiftBrowserConfig(AppConfig):
    name = 'swiftbrowser'
    verbose_name = _("Swift Browser")
    dashboard_widgets = [{'widget_class': 'swiftbrowser.widgets.SwiftWidget'}]
