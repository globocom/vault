# -*- coding:utf-8 -*-

from django import template
from django.template.loader import render_to_string


register = template.Library()


@register.tag
def selectproject(parser, token):
    """ Select project dropdown menu """

    return SelectProject()


class SelectProject(template.Node):

    def render(self, context):
        user = context.get('logged_user')
        projects = []

        if user:
            try:
                projects = user.authorized_tenants
            except AttributeError:
                pass

        return render_to_string('identity/select_project.html',
                                {'projects': projects})
