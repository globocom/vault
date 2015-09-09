# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('vault/projectsandusers.html', takes_context=True)
def show_projectsandusers(context):

    return {'user': context.get('user')}
