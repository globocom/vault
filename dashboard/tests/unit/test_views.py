# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

from vault.tests.fakes import fake_request
from dashboard.views import DashboardView

# from identity.keystone import Keystone
from identity.tests.fakes import FakeToken

from swiftbrowser.tests import fakes


def fake_get_account():

    account_stat = {
        'content-length': '147',
        'x-account-object-count': '5',
        'server': 'nginx',
        'connection': 'keep-alive',
        'x-timestamp': '1405090896.54396',
        'x-account-meta-temp-url-key': 'ipytkrl2sij2gbycz10xrem23hfsz3z4',
        'x-trans-id': 'tx11e34a0efd904a7cbd6e7-0053f49d36',
        'date': 'Wed, 20 Aug 2014 13:05:58 GMT',
        'x-account-bytes-used': '46',
        'x-account-container-count': '3',
        'content-type': 'application/json; charset=utf-8',
        'accept-ranges': 'bytes'
    }

    containers = [
        {'count': 4, 'bytes': 32, 'name': 'container1'},
        {'count': 0, 'bytes': 0, 'name': 'container2'},
        {'count': 1, 'bytes': 14, 'name': 'container3'}
    ]

    return (account_stat, containers)


class DashboardTest(TestCase):

    def setUp(self):
        self.view = DashboardView.as_view()

        self.request = fake_request(method='GET')
        self.request.user.is_authenticated = lambda: True
        self.request.user.token = FakeToken()
        self.request.user.service_catalog = [
            {
                u'endpoints': [{
                    u'adminURL': u'https://fakeurl',
                    u'region': u'RegionOne',
                    u'id': u'fakeid',
                    u'internalURL': u'https://fakeurl',
                    u'publicURL': u'http://fakeurl'
                }],
                u'endpoints_links': [],
                u'type': u'object-store',
                u'name': u'swift'
            },
            {
                u'endpoints': [{
                    u'adminURL': u'https://fakeurl',
                    u'region': u'RegionOne',
                    u'id': u'fakeid',
                    u'internalURL': u'https://fakeurl',
                    u'publicURL': u'https://fakeurl',
                }],
                u'endpoints_links': [],
                u'type': u'identity',
                u'name': u'keystone'
            }
        ]

        patch('dashboard.views.Keystone._keystone_conn',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_dashboard_will_redirect_to_login_if_not_logged(self):
        self.request.method = 'POST'
        self.request.build_absolute_uri = lambda: '/'
        self.request.user.is_authenticated = lambda: False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    @patch('dashboard.views.DashboardView._widget_storage')
    @patch('dashboard.views.Keystone.user_list')
    def test_widget_users(self, mock_user_list, mock__widget_storage):

        mock_user_list.return_value = [1]
        mock__widget_storage.return_value = False

        response = self.view(self.request)
        response.render()

        self.assertIn('widget-users', response.content)
        self.assertIn('<span class="info">total&nbsp;users</span>', response.content)
        self.assertIn('<span class="number">1</span>', response.content)

    @patch('dashboard.views.DashboardView._widget_users')
    @patch('swiftbrowser.views.client.get_account')
    def test_widget_storage(self, mock_get_account, mock__widget_users):

        mock_get_account.return_value = fake_get_account()
        mock__widget_users.return_value = False

        response = self.view(self.request)
        response.render()

        self.assertIn('widget-storage', response.content)
        self.assertIn('Containers <span class="number">3</span>', response.content)
        self.assertIn('Objects <span class="number">5</span>', response.content)

    @patch('dashboard.views.DashboardView._widget_users')
    @patch('dashboard.views.DashboardView._widget_storage')
    def test_show_identity_menu_for_superuser(self, mock__widget_storage, mock__widget_users):

        mock__widget_storage.return_value = False
        mock__widget_users.return_value = False

        self.request.user.is_superuser = True

        response = self.view(self.request)
        response.render()

        self.assertIn('Identity', response.content)

    @patch('dashboard.views.DashboardView._widget_users')
    @patch('dashboard.views.DashboardView._widget_storage')
    def test_hide_identity_menu_for_not_superuser(self, mock__widget_storage, mock__widget_users):

        mock__widget_storage.return_value = False
        mock__widget_users.return_value = False
        self.request.user.is_superuser = False

        response = self.view(self.request)
        response.render()

        self.assertNotIn('Identity', response.content)
