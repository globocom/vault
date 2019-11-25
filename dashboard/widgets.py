# -*- coding: utf-8 -*-

import logging

from django import template
from django.apps import apps
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string


log = logging.getLogger(__name__)


class RenderWidgets(template.Node):
    widgets = []
    sizes = {
        "tiny": "col-md-2 col-xs-4",
        "small": "col-md-4 col-xs-4",
        "half": "col-md-6 col-xs-6",
        "big": "col-md-8 col-xs-12",
        "full": "col-md-12 col-xs-12"
    }

    def __init__(self, *args, **kwargs):
        for conf in apps.get_app_configs():
            if hasattr(conf, 'dashboard_widgets'):
                self.widgets = self.widgets + conf.dashboard_widgets
        super(RenderWidgets, self).__init__(*args, **kwargs)

    def render(self, context):
        content = ['<ul class="dashboard-widgets">']

        for item in self.widgets:
            WidgetClass = self._get_widget_cls(item['widget_class'])
            widget = WidgetClass(context)

            if widget.check_visibility():
                content.append(self._build_widget(widget))

        content = '{}</ul>'.format(''.join(content).encode('utf-8'))

        return content

    def _build_widget(self, widget):
        size = self.sizes.get("half")
        if widget.size in self.sizes:
            size = self.sizes.get(widget.size)

        return u'<li class="widget {}">{}</li>'.format(size, widget.render())

    def _get_widget_cls(self, cl):
        d = cl.rfind(".")
        classname = cl[d + 1:len(cl)]
        m = __import__(cl[0:d], globals(), locals(), [classname])
        return getattr(m, classname)


class BaseWidget(object):
    widget_template = 'dashboard/widgets/widget.html'
    size = "half"

    def __init__(self, context):
        self.context = context

    @property
    def is_visible(self):
        return True

    @property
    def has_team(self):
        user = self.context.get('user')
        return user.groups.count() > 0

    def check_visibility(self):
        return self.has_team and self.is_visible

    def get_widget_context(self):
        return {}

    def _full_context(self):
        ctx = self.get_widget_context()
        ctx.update({
            'user': self.context.get('logged_user'),
            'project_id': self.context.get('project_id')
        })
        return ctx

    def render(self):
        return render_to_string(self.widget_template, self._full_context())


class NoTeamWarning(BaseWidget):
    widget_template = 'dashboard/widgets/noteam.html'
    size = "full"

    @property
    def has_team(self):
        user = self.context.get('user')
        return user.groups.count() <= 0
