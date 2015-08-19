# coding: utf-8

from django.template.loader import render_to_string

from dashboard.widgets import BaseWidget
from vault.models import GroupProjects


class ProjectsWidget(BaseWidget):
    title = "Projects"
    subtitle = "Object Storage"
    # TODO: revisar problema de unicode (cedilha e til)
    description = "Relacao de projetos gerenciados pelo seu time"
    content_template = 'swiftbrowser/select_project.html'

    def get_widget_context(self):
        user = self.context.get('logged_user')
        groups = user.groups.all()
        group_projects = GroupProjects.objects.filter(group__in=groups)

        return {'projects': [gp.project for gp in group_projects]}
