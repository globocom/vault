# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import patch
from keystoneclient.openstack.common.apiclient import exceptions

from django.conf import settings

from identity.keystone import Keystone, UnauthorizedProject
from identity.tests.fakes import FakeKeystone, UserFactory, ProjectFactory, GroupFactory, FakeResource, AreaFactory
from vault.tests.fakes import fake_request


class TestKeystoneV2(TestCase):
    """ Test keystone version 2 """

    def setUp(self):
        self.user = UserFactory()
        self.request = fake_request(user=self.user)

        self.group = GroupFactory(id=1)
        self.area = AreaFactory(id=1)

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
    def test_vault_create_project(self, mock_gp, mock_ap, mock_key_pass, mock_key_user, mock_project_create, __, mock_project, _):
        mock_project.return_value = ProjectFactory()

        project_id = 'abcdefghiklmnopq'
        project_name = 'project_test'
        project_desc = 'project description'

        mock_project_create.return_value = ProjectFactory(id=project_id, name=project_name)
        mock_key_user.return_value = FakeResource(n=project_id, name='u_{}'.format(project_name))
        mock_key_pass.return_value = 'password'

        keystone = Keystone(self.request, 'tenant_name')

        expected = {
            'status': True,
            'project': mock_project_create.return_value,
            'user': mock_key_user.return_value,
            'password': mock_key_pass.return_value,
        }

        computed = keystone.vault_create_project(project_name, self.group, self.area, description=project_desc)

        # Criacao do Project
        mock_project_create.assert_called_with(project_name, description=project_desc, enabled=True)

        # Criacao do User
        mock_key_user.assert_called_with(name='u_{}'.format(project_name),
                                         password='password',
                                         project=project_id,
                                         role=settings.ROLE_BOLADONA)

        mock_gp.assert_called_with(group=self.group, project=mock_project_create.return_value)
        self.assertTrue(mock_gp.return_value.save.called)

        mock_ap.assert_called_with(area=self.area, project=mock_project_create.return_value )
        self.assertTrue(mock_gp.return_value.save.called)

        self.assertEqual(computed, expected)

    @patch('identity.keystone.GroupProjects.objects.filter')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Keystone.project_create')
    @patch('identity.keystone.Keystone.user_create')
    def test_vault_create_project_forbidden_on_project_create(self, mock_key_user, mock_key_proj, __, mock_project, _):
        mock_project.return_value = ProjectFactory()

        project_id = 'abcdefghiklmnopq'
        project_name = 'project_test'
        project_desc = 'project description'

        mock_key_proj.side_effect = exceptions.Forbidden
        mock_key_user.return_value = FakeResource(n=project_id, name='u_{}'.format(project_name))

        keystone = Keystone(self.request, 'tenant_name')

        expected = {'status': False, 'reason': 'Admin required'}
        computed = keystone.vault_create_project(project_name, self.group, self.area, description=project_desc)

        self.assertEqual(computed, expected)

        # Criacao de user nao pode ocorrer quando hover falha na criacao do project
        self.assertFalse(mock_key_user.called)

    @patch('identity.keystone.GroupProjects.objects.filter')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Keystone.project_create')
    @patch('identity.keystone.Keystone.project_delete')
    @patch('identity.keystone.Keystone.user_create')
    def test_vault_create_project_forbidden_on_user_create(self, mock_key_user, mock_project_delete, mock_project_create, __, mock_project, _):
        mock_project.return_value = ProjectFactory()

        project_id = 'abcdefghiklmnopq'
        project_name = 'project_test'
        project_desc = 'project description'

        mock_project_create.return_value = ProjectFactory(id=project_id, name=project_name)
        mock_key_user.side_effect = exceptions.Forbidden

        keystone = Keystone(self.request, 'tenant_name')

        expected = {'status': False, 'reason': 'Admin required'}
        computed = keystone.vault_create_project(project_name, self.group, self.area, description=project_desc)

        self.assertEqual(computed, expected)

        # Se falhou o cadastro de usuario, o project devera ser deletado
        mock_project_delete.assert_called_with(project_id)

    @patch('identity.keystone.GroupProjects.objects.filter')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.Keystone.project_create')
    @patch('identity.keystone.Keystone.project_delete')
    @patch('identity.keystone.Keystone.user_create')
    @patch('identity.keystone.Keystone.user_delete')
    @patch('identity.keystone.GroupProjects.save')
    def test_vault_create_project_fail_to_save_group_project_on_db(self, mock_gp_save, mock_user_delete, mock_user_create, mock_project_delete, mock_project_create, mock_keystone_conn, mock_project, _):
        mock_project.return_value = ProjectFactory()

        project_id = 'abcdefghiklmnopq'
        project_name = 'project_test'
        project_desc = 'project description'

        mock_project_create.return_value = ProjectFactory(id=project_id, name=project_name)
        fake_user = FakeResource(n=project_id, name='u_{}'.format(project_name))
        mock_user_create.return_value = fake_user

        # Excecao ao salvar no db
        mock_gp_save.side_effect = Exception

        keystone = Keystone(self.request, 'tenant_name')

        expected = {'status': False, 'reason': 'Unable to assign project to group'}
        computed = keystone.vault_create_project(project_name, self.group, self.area, description=project_desc)

        self.assertEqual(computed, expected)

        mock_project_delete.assert_called_with(project_id)
        mock_user_delete.assert_called_with(fake_user.id)

    @patch('identity.keystone.Keystone._keystone_conn')
    @patch('identity.keystone.AreaProjects')
    @patch('identity.keystone.Project.objects.get')
    @patch('identity.keystone.GroupProjects.objects.filter')
    @patch('identity.keystone.GroupProjects.save')
    def test_vault_create_project_fail_to_save_project_to_team_on_db(self, mock_gp_save, mock_gp_objects, mock_project, mock_areaprojects, mock_keystone_conn):
        mock_keystone_conn.return_value.tenants.create.return_value = ProjectFactory()
        mock_areaprojects.side_effect = Exception
        mock_project.return_value = ProjectFactory()
        mock_gp_objects.return_value = []
        project_name = 'project_test'
        keystone = Keystone(self.request, 'tenant_name')
        result = keystone.vault_create_project(project_name, self.group, self.area)
        expected = {'status': False, 'reason': 'Unable to assign project to area'}
        self.assertEqual(result, expected)


    def test_create_password(self):

        computed = Keystone.create_password()

        self.assertTrue(isinstance(computed, str))
