# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import patch
from keystoneclient.openstack.common.apiclient import exceptions

from django.conf import settings

from identity.keystone import Keystone, UnauthorizedProject
from identity.tests.fakes import FakeKeystone, UserFactory, ProjectFactory, FakeResource
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

    @patch('identity.keystone.GroupProjects.objects.filter')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Keystone.project_create')
    @patch('identity.keystone.Keystone.user_create')
    @patch('identity.keystone.Keystone.create_password')
    @patch('identity.keystone.AreaProjects')
    @patch('identity.keystone.GroupProjects')
    def test_vault_create_project(self, mock_go, mock_ap, mock_key_pass, mock_key_user, mock_key_proj, mock_key_conn, mock_project, _):
        mock_project.return_value = ProjectFactory()

        project_id = 'abcdefghiklmnopq'
        project_name = 'project_test'
        project_desc = 'project description'

        mock_key_proj.return_value = ProjectFactory(id=project_id, name=project_name)
        mock_key_user.return_value = FakeResource(n=project_id, name=project_name)
        mock_key_pass.return_value = 'password'

        keystone = Keystone(self.request, 'tenant_name')

        keystone.vault_create_project(project_name, 1, 1, description=project_desc)

        # Criacao do Project
        mock_key_proj.assert_called_with(project_name, description=project_desc, enabled=True)

        # Criacao do User
        mock_key_user.assert_called_with(name='u_{}'.format(project_name),
                                         password='password',
                                         project=project_id,
                                         role=settings.ROLE_BOLADONA)


        mock_go.assert_called_with(group=1, project=project_id)
        self.assertTrue(mock_go.return_value.save.called)

        mock_ap.assert_called_with(area=1, project=project_id)
        self.assertTrue(mock_go.return_value.save.called)\

    @patch('identity.keystone.GroupProjects.objects.filter')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Keystone.project_create')
    @patch('identity.keystone.Keystone.user_create')
    def test_vault_create_project_fail_on_project_create(self, mock_key_user, mock_key_proj, mock_key_conn, mock_project, _):
        mock_project.return_value = ProjectFactory()

        project_id = 'abcdefghiklmnopq'
        project_name = 'project_test'
        project_desc = 'project description'

        mock_key_proj.side_effect = exceptions.Forbidden
        mock_key_user.return_value = FakeResource(n=project_id, name=project_name)

        keystone = Keystone(self.request, 'tenant_name')

        expected = {'status': 403, 'reason': 'Admin required'}
        computed = keystone.vault_create_project(project_name, 1, 1, description=project_desc)

        self.assertEqual(computed, expected)

        # Criacao de user nao pode ocorrer quando hover falha na criacao do project
        self.assertFalse(mock_key_user.called)

    def test_create_password(self):

        computed = Keystone.create_password()

        self.assertTrue(isinstance(computed, str))
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
