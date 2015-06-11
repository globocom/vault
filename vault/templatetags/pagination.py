# -*- coding:utf-8 -*-

from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.inclusion_tag('vault/pagination.html')
def pagination(paginated_item):
    return {'items': paginated_item}
