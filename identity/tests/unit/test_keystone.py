# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import patch

from identity.keystone import Keystone, UnauthorizedProject
from identity.tests.fakes import FakeKeystone, UserFactory, ProjectFactory
from vault.tests.fakes import fake_request


class TestKeystoneV2(TestCase):
    """ Test keystone version 2 """

    #@patch('identity.keystone.Keystone._keystone_conn')
    def setUp(self):

        #self.mock_keystone_conn = mock_keystone_conn

        self.user = UserFactory()

        self.request = fake_request(user=self.user)

        #mock_keystone_conn.return_value = FakeKeystone(self.request)

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.GroupProjects.objects.filter')
    def test_superuser_creates_keystone_conn(self, mock_filter, mock_project, _):
        mock_filter.return_value = None
        mock_project.return_value = ProjectFactory()
        self.conn = Keystone(self.request, 'tenant_id')
        self.assertTrue(isinstance(self.conn, Keystone))


    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.GroupProjects.objects.filter')
    def test_regular_user_creates_keystone_conn_on_a_allowed_project(self, mock_filter, mock_project, _):

        # Se este mock retorna uma lista nao vazia, significa que o time do project
        # usuario possui permissao no project
        mock_filter.return_value = [1]
        mock_project.return_value = ProjectFactory()

        self.request.user.is_superuser = False
        self.conn = Keystone(self.request, 'tenant_id')

        self.assertTrue(isinstance(self.conn, Keystone))

    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.GroupProjects.objects.filter')
    def test_regular_user_creates_keystone_conn_on_a_NOT_allowed_project(self, mock_filter, mock_project, _):

        # Se este mock retorna uma lista  vazia, significa que o time do project
        # usuario NAO possui permissao no project
        mock_filter.return_value = []
        mock_project.return_value = ProjectFactory()
        self.request.user.is_superuser = False

        self.assertRaises(UnauthorizedProject, Keystone, self.request, 'tenant_id')

    # def test_get_endpoint_keystone_v2(self):
    #     self.conn = Keystone(self.request)
    #     self.assertEqual(self.conn._get_keystone_endpoint(), u'https://adminURL.com:35357/v2.0')

    # def test_user_get_v2(self):
    #     self.conn = Keystone(self.request)
    #     user_managed = self.conn.user_get(self.request.user)
    #     self.assertEqual(user_managed.project_id, self.request.user.tenantId)


# class TestKeystoneV3(TestCase):
#     """ Test keystone version 3 """

#     def setUp(self):
#         patch('identity.keystone.Keystone._keystone_conn',
#               Mock(return_value=None)).start()

#         patch('identity.keystone.settings',
#             KEYSTONE_VERSION=3).start()

#         self.user = FakeResource(1, 'user')
#         self.user.is_superuser = True
#         self.user.is_authenticated = lambda: True
#         self.user.token = FakeToken
#         self.user.project_id = 1
#         self.user.service_catalog = [
#             {
#                 u'endpoints': [
#                     {
#                         u'url': u'http://public/v1/AUTH_123',
#                         u'interface': u'public',
#                         u'region': u'RegionOne',
#                         u'id': u'a3811ec073ea4e22bfc8be015c3d681c'
#                     },
#                     {
#                         u'url': u'https://admin/v1',
#                         u'interface': u'admin',
#                         u'region': u'RegionOne',
#                         u'id': u'a3dc6f4ed32f4685b512dc2bcc913bd8'
#                     },
#                     {
#                         u'url': u'https://internal/v1/AUTH_123',
#                         u'interface': u'internal',
#                         u'region': u'RegionOne',
#                         u'id': u'b35f042b3e6944c68319d2ed59377902'
#                     }
#                 ],
#                 u'type': u'object-store',
#                 u'id': u'7efb509d3a0b446fa324d0bc4503e6d3'
#             },
#             {
#                 u'endpoints': [
#                     {
#                         u'url': u'https://public:5000/v3',
#                         u'interface': u'public',
#                         u'region': u'RegionOne',
#                         u'id': u'190aec2eb33b44e98f01f64fe30dfcff'
#                     },
#                     {
#                         u'url': u'https://internal:35357/v3',
#                         u'interface': u'internal',
#                         u'region': u'RegionOne',
#                         u'id': u'a6ccd0b8f1a34a85ab5588f86037241a'
#                     },
#                     {
#                         u'url': u'https://admin:35357/v3',
#                         u'interface': u'admin',
#                         u'region': u'RegionOne',
#                         u'id': u'be411d86d86b4390a8b1ce4c9804e331'
#                     }
#                 ],
#                 u'type': u'identity',
#                 u'id': u'c1532ec33ada4417a8ade53ee2cd8fd4'
#             }
#         ]

#         self.request = fake_request(user=self.user)

#     def tearDown(self):
#         patch.stopall()

#     @patch('identity.keystone.Keystone._keystone_conn')
#     def test_get_endpoint_keyston_v3(self, mock_keystone_conn):

#         conn = Keystone(self.request)
#         self.assertEqual(conn._get_keystone_endpoint(), u'https://admin:35357/v3')

#     @patch('identity.keystone.Keystone._keystone_conn')
#     def test_user_manager_v3(self, mock_keystone_conn):

#         conn = Keystone(self.request)
#         user_managed = conn._user_manager(self.request.user)

#         self.assertEqual(user_managed.project_id, self.request.user.project_id)
