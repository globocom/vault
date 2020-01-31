# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest.mock import Mock, patch

from vault.tests.fakes import fake_request, UserFactory
from dashboard.views import DashboardView


class DashboardTest(TestCase):

    def setUp(self):
        self.view = DashboardView.as_view()
        self.request = fake_request(method='GET')
        self.request.user = UserFactory(id='999', username='u_user_test')

        # does not connect to the keystone client
        patch('keystoneclient.v2_0.client.Client').start()

    def tearDown(self):
        patch.stopall()

    def test_dashboard_needs_authentication(self):
        req = fake_request(method='GET')
        response = self.view(req)
        self.assertEqual(response.status_code, 302)

    def test_show_dashboard(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 200)

        response.render()
        self.assertIn(b'Dashboard', response.content)
