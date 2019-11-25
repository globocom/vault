# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from dashboard.widgets import RenderWidgets


register = template.Library()


@register.tag
def render_widgets(parser, token):
    """Templatetag to render dashboard widgets"""

    return RenderWidgets()
