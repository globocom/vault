# -*- coding:utf-8 -*-

from django import template
from django.template.loader import render_to_string

from vault.models import GroupProjects


register = template.Library()


@register.tag
def selectproject(parser, token):
    """ Select project dropdown menu """

    return SelectProject()


class SelectProject(template.Node):

    def render(self, context):
        user = context.get('logged_user')

        groups = user.groups.all()
        group_projects = GroupProjects.objects.filter(group__in=groups)

        projects = [gp.project for gp in group_projects]

        return render_to_string('identity/select_project.html',
                                {'projects': projects})
