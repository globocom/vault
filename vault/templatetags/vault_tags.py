import json

from urllib.parse import urlencode
from django import template
from django.conf import settings
from django.apps import apps

from vault.models import GroupProjects
from identity.keystone import KeystoneNoRequest

register = template.Library()


@register.simple_tag(takes_context=True)
def get_vault_env(context):
    request = context.get("request")
    envs = ["dev", "qa", "qa1", "qa2", "prod", "beta", "docker"]

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
        gps_ks = [x for x in
                filter(lambda x: x.enabled, keystone.project_list())]
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


@register.simple_tag()
def url_replace(get_parameters, **kwargs):
    query = get_parameters
    query.update(kwargs)
    for x in query:
        if type(query[x]) is not list:
            query[x] = [query[x]]
    query_pairs = [(k, v) for k, vlist in query.items() for v in vlist]
    return urlencode(query_pairs)
