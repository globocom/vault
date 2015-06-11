# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

from identity.keystone import Keystone
from identity.tests.fakes import FakeResource, FakeToken, FakeKeystone
from vault.tests.fakes import fake_request


class TestKeystoneV2(TestCase):
    """ Test keystone version 2 """

    @patch('identity.keystone.Keystone._keystone_conn')
    def setUp(self, mock_keystone_conn):

        self.mock_keystone_conn = mock_keystone_conn

        patch('identity.keystone.settings',
            KEYSTONE_VERSION=2).start()

        self.user = FakeResource(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated = lambda: True
        self.user.token = FakeToken
        self.user.tenantId = 1
        self.user.project_id = None
        self.user.service_catalog = [
            {
                u'endpoints': [{
                    u'adminURL': u'https://adminURL.com/v1',
                    u'region': u'RegionOne',
                    u'id': u'a3811ec073ea4e22bfc8be015c3d681c',
                    u'internalURL': u'https://internalURL.com/v1/AUTH_123',
                    u'publicURL': u'http://publicURL.com/v1/AUTH_123'
                }],
                u'endpoints_links': [],
                u'type': u'object-store',
                u'name': u'swift'
            },
            {
                u'endpoints': [{
                    u'adminURL': u'https://adminURL.com:35357/v2.0',
                    u'region': u'RegionOne',
                    u'id': u'190aec2eb33b44e98f01f64fe30dfcff',
                    u'internalURL': u'https://internalURL.com:35357/v2.0',
                    u'publicURL': u'https://publicURL.com:5000/v2.0'
                }],
                u'endpoints_links': [],
                u'type': u'identity',
                u'name': u'keystone'
            }
        ]

        self.request = fake_request(user=self.user)

        mock_keystone_conn.return_value = FakeKeystone(self.request)

        self.conn = Keystone(self.request)

    def tearDown(self):
        patch.stopall()

    def test_get_endpoint_keystone_v2(self):
        self.assertEqual(self.conn._get_keystone_endpoint(), u'https://adminURL.com:35357/v2.0')

    def test_user_get_v2(self):
        user_managed = self.conn.user_get(self.request.user)
        self.assertEqual(user_managed.project_id, self.request.user.tenantId)


class TestKeystoneV3(TestCase):
    """ Test keystone version 3 """

    def setUp(self):
        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        patch('identity.keystone.settings',
            KEYSTONE_VERSION=3).start()

        self.user = FakeResource(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated = lambda: True
        self.user.token = FakeToken
        self.user.project_id = 1
        self.user.service_catalog = [
            {
                u'endpoints': [
                    {
                        u'url': u'http://public/v1/AUTH_123',
                        u'interface': u'public',
                        u'region': u'RegionOne',
                        u'id': u'a3811ec073ea4e22bfc8be015c3d681c'
                    },
                    {
                        u'url': u'https://admin/v1',
                        u'interface': u'admin',
                        u'region': u'RegionOne',
                        u'id': u'a3dc6f4ed32f4685b512dc2bcc913bd8'
                    },
                    {
                        u'url': u'https://internal/v1/AUTH_123',
                        u'interface': u'internal',
                        u'region': u'RegionOne',
                        u'id': u'b35f042b3e6944c68319d2ed59377902'
                    }
                ],
                u'type': u'object-store',
                u'id': u'7efb509d3a0b446fa324d0bc4503e6d3'
            },
            {
                u'endpoints': [
                    {
                        u'url': u'https://public:5000/v3',
                        u'interface': u'public',
                        u'region': u'RegionOne',
                        u'id': u'190aec2eb33b44e98f01f64fe30dfcff'
                    },
                    {
                        u'url': u'https://internal:35357/v3',
                        u'interface': u'internal',
                        u'region': u'RegionOne',
                        u'id': u'a6ccd0b8f1a34a85ab5588f86037241a'
                    },
                    {
                        u'url': u'https://admin:35357/v3',
                        u'interface': u'admin',
                        u'region': u'RegionOne',
                        u'id': u'be411d86d86b4390a8b1ce4c9804e331'
                    }
                ],
                u'type': u'identity',
                u'id': u'c1532ec33ada4417a8ade53ee2cd8fd4'
            }
        ]

        self.request = fake_request(user=self.user)

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone._keystone_conn')
    def test_get_endpoint_keyston_v3(self, mock_keystone_conn):

        conn = Keystone(self.request)
        self.assertEqual(conn._get_keystone_endpoint(), u'https://admin:35357/v3')

    @patch('identity.keystone.Keystone._keystone_conn')
    def test_user_manager_v3(self, mock_keystone_conn):

        conn = Keystone(self.request)
        user_managed = conn._user_manager(self.request.user)

        self.assertEqual(user_managed.project_id, self.request.user.project_id)
