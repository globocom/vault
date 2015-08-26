# -*- coding:utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('vault/pagination.html')
def pagination(paginated_item):
    return {'items': paginated_item}
