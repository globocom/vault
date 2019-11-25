# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DashboardConfig(AppConfig):
    name = 'dashboard'
    verbose_name = _("Dashboard")
    dashboard_widgets = [{'widget_class': 'dashboard.widgets.NoTeamWarning'}]
