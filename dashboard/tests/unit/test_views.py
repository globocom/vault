# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import patch

from vault.tests.fakes import fake_request
from dashboard.views import DashboardView


class DashboardTest(TestCase):

    def setUp(self):
        self.view = DashboardView.as_view()
        self.request = fake_request(method='GET')
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_authenticated = lambda: True

    def tearDown(self):
        patch.stopall()

    def test_dashboard_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False
        response = self.view(self.request)
        self.assertEqual(response.status_code, 302)

    def test_show_dashboard(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 200)

        response.render()
        self.assertIn('Dashboard', response.content)
