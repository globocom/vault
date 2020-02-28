# -*- coding: utf-8 -*-

import logging

from datetime import datetime

from django import template
from django.utils.timezone import utc
from django.template.defaultfilters import stringfilter

from storage.views.backup import get_current_backup


register = template.Library()
log = logging.getLogger(__name__)


@register.inclusion_tag("storage/storage_tools.html", takes_context=True)
def storage_tools(context):
    meta = context.get('container_meta')
    container = context.get("container")
    project_id = context.get("project_id")
    project_name = context.get("project_name")

    trash_enabled = meta.get('x-undelete-enabled')
    if trash_enabled is None or trash_enabled == 'False':
        trash_enabled = False

    return {
        'trash_enabled': trash_enabled,
        'backup_obj': get_current_backup(container, project_id),
        'container': container,
        'prefix': context.get('prefix'),
        'project_id': project_id,
        'project_name': project_name
    }


@register.filter
@stringfilter
def lastpart(value):
    value = value.strip('/').split('/')[-1]
    return value


@register.filter
@stringfilter
def dateconv(value):
    try:
        value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        value = value.replace(tzinfo=utc)
    except ValueError:
        value = 0.0
    return value
