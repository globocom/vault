# -*- coding: utf-8 -*-

from django import template
from django.apps import apps
from django.conf import settings


register = template.Library()


@register.simple_tag
def info_endpoints():
    """Templatetag to render a list of info endpoints"""

    endpoints = []

    for conf in apps.get_app_configs():
        if hasattr(conf, 'app_name'):
            endpoints.append("'/{}/api/info'".format(conf.name))

    return ','.join(endpoints)
