# coding: utf-8

from django.template.loader import render_to_string

from dashboard.widgets import BaseWidget
from vault.models import GroupProjects


class ProjectsWidget(BaseWidget):
    title = "Projects"
    subtitle = "Object Storage"
    # TODO: revisar problema de unicode (cedilha e til)
    description = "Relacao de projetos gerenciados pelo seu time"
    content_template = 'swiftbrowser/widgets/select_project.html'
    non_renderable_template = 'swiftbrowser/widgets/non_renderable.html'

    def __init__(self, context):
        self.user = context.get('logged_user')
        return super(ProjectsWidget, self).__init__(context)

    def get_widget_context(self):
        groups = self.user.groups.all()
        group_projects = GroupProjects.objects.filter(group__in=groups)

        return {'projects': [gp.project for gp in group_projects]}

    @property
    def renderable(self):
        return self.user.groups.count() > 0
