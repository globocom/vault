# -*- coding: utf-8 -*-

import json
from django import template
from django.apps import apps
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def info_endpoints(context, **kwargs):
    """Templatetag to render a list of info endpoints"""

    endpoints = []
    request = context.get('request')
    project_name = request.session.get('project_name')

    for conf in apps.get_app_configs():
        if hasattr(conf, 'vault_app'):
            endpoints.append(
                "/p/{}/{}/api/info".format(project_name, conf.name))

    return json.dumps(endpoints)
