# coding: utf-8

from unittest import TestCase
from mock import patch

from vault.tests.fakes import fake_request
from swiftbrowser.widgets import ProjectsWidget


class DummyGP(object):
    project = None

    def __init__(self, project):
        self.project = project


class SwftbrowserWidgetsTest(TestCase):

    def setUp(self):
        self.request = fake_request(method='GET')
        self.request.user.is_authenticated = lambda: True

    @patch('swiftbrowser.widgets.GroupProjects.objects.filter')
    def test_check_projects_in_context_of_projects_widget(self, mock_projects):
        mock_projects.return_value = [DummyGP(1), DummyGP(2)]

        prjwidget = ProjectsWidget({})
        content = prjwidget.render()

        template = self.view(self.request)

        self.assertEqual(template.context_data['projects'], [1, 2])
