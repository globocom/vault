# -*- coding: utf-8 -*-

from urllib import urlencode
from django import template
from django.conf import settings

from vault.models import GroupProjects
from identity.keystone import KeystoneNoRequest

import requests
import json


register = template.Library()


@register.simple_tag(takes_context=True)
def with_sidebar(context):
    req = context.get("request")
    body_cls = ""
    if req.COOKIES.get("show_sidebar"):
        body_cls = "with-sidebar "

    return body_cls


@register.simple_tag(takes_context=True)
def get_vault_env(context):
    request = context.get("request")
    envs = ["dev", "qa", "qa1", "qa2", "prod"]

    if settings.ENVIRON in envs:
        return settings.ENVIRON

    if settings.ENVIRON is None and "localhost" in request.get_host():
        return "local"

    return ""


@register.inclusion_tag('vault/set_project.html', takes_context=True)
def set_project(context):
    user = context.get('user')
    groups = user.groups.all()
    request = context.get('request')
    keystone = KeystoneNoRequest()
    group_projects = []

    for group in groups:
        gps = GroupProjects.objects.filter(group=group.id)
        gps_ks = filter(lambda x: x.enabled, keystone.project_list())
        gp_projs = []

        for gp in gps:
            for gp_ks in gps_ks:
                if gp.project == gp_ks.id:
                    gp_projs.append(gp_ks)
                    break

        gp_projs.sort(key=lambda x: x.name.lower())
        group_projects.append({
            'team': group.name,
            'projects': gp_projs
        })

    current_project = {'id': context.get('project_id'),
                       'name': context.get('project_name')}

    if current_project.get('id') is None:
        req = context.get('request')
        current_project['id'] = req.session.get('project_id')
        current_project['name'] = req.session.get('project_name')

    return {
        'current_project': current_project,
        'group_projects': group_projects,
        'has_group': user.groups.count() > 0
    }


@register.simple_tag(takes_context=True)
def get_logout_url(context):
    request = context.get('request')
    logout_url = settings.LOGOUT_URL.format(
        request.META['HTTP_HOST']
    )
    return logout_url


@register.assignment_tag(takes_context=True)
def can_view_team_users_ogs(context):
    user = context.get('user')
    add_og = False
    change_og = False
    delete_og = False

    if len(user.groups.all()) == 0:
        return (add_og and change_og and delete_og)

    group = user.groups.all()[0]

    for permission in group.permissions.all():
        try:
            codename = permission.codename
            exec(codename + ' = True')
        except Exception:
            pass

    return (add_og and change_og and delete_og)


@register.simple_tag()
def url_replace(get_parameters, **kwargs):
    query = get_parameters
    query.update(kwargs)
    return urlencode(query)
