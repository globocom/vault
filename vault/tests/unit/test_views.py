# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

from vault.tests.fakes import fake_request
from vault.views import SetProjectView


class SetProjectTest(TestCase):

    def setUp(self):
        self.view = SetProjectView.as_view()
        self.request = fake_request(method='GET')
        self.request.user.is_authenticated = lambda: False

    def tearDown(self):
        patch.stopall()

    def test_set_project_needs_authentication(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 302)

    @patch('vault.views.switch')
    def test_set_new_project_id_to_session(self, mock_switch):
        self.request.user.is_authenticated = lambda: True
        self.assertEqual(self.request.session.get('project_id'), '1')

        response = self.view(self.request, project_id=2)
        self.assertEqual(self.request.session.get('project_id'), 2)

    @patch('vault.views.switch')
    def test_set_new_project_id_to_session_exception(self, mock_switch):
        self.request.user.is_authenticated = lambda: True
        mock_switch.side_effect = ValueError()

        self.assertEqual(self.request.session.get('project_id'), '1')

        response = self.view(self.request, project_id=2)
        self.assertEqual(self.request.session.get('project_id'), 2)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, 'Unable to change your project.')
