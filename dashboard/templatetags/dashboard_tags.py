# -*- coding: utf-8 -*-

from django import template
from django.apps import apps
from django.conf import settings

from dashboard.widgets import RenderWidgets


register = template.Library()


@register.tag
def render_widgets(parser, token):
    """Templatetag to render dashboard widgets"""

    return RenderWidgets()


@register.simple_tag
def info_endpoints():
    """Templatetag to render a list of info endpoints"""

    endpoints = []

    for conf in apps.get_app_configs():
        if hasattr(conf, 'info_endpoint'):
            endpoints.append("'" + conf.info_endpoint + "'")

    return ','.join(endpoints)
