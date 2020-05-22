# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.inclusion_tag('vault/pagination.html', takes_context=True)
def pagination(context, paginated_item):
    return {
        'items': paginated_item,
        'get_parameters': dict(context['request'].GET)
    }
