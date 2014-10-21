# -*- coding:utf-8 -*-

from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.inclusion_tag('pagination.html')
def pagination(paginated_item):
    return {'items': paginated_item}

# @register.tag
# def pagination(parser, token):
#     import ipdb;ipdb.set_trace()
#     try:
#         # split_contents() knows not to split quoted strings.
#         paginated_item = token.split_contents()
#     except ValueError:
#         raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])

#     return Paginate(paginated_item)


# class Paginate(template.Node):

#     def __init__(self, paginated_item):
#         self.paginated_item = paginated_item

#     def render(self, context):
#         user = context.get('logged_user')
#         projects = []

#         import ipdb;ipdb.set_trace()

#         return render_to_string('pagination.html', {'items': self.paginated_item})
