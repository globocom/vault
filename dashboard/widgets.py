
from django.conf import settings
from django.template.loader import render_to_string


class BaseWidget(object):
    title = 'Widget'
    description = 'Widget Description'
    content_template = 'dashboard/widgets/content.html'

    def __init__(self, context):
        self.context = context

    def get_widget_context(self):
        return {}

    def _full_context(self):
        widget_context = self.get_widget_context()
        widget_context.update({
            'title': self.title,
            'description': self.description,
            'content_template': self.content_template
        })

        return widget_context

    def render(self):
        return render_to_string('dashboard/widgets/full.html',
                                self._full_context())
