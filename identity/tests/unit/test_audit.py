# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

from identity.views import ListUserView, ListUserRoleView, CreateUserView, UpdateUserView, DeleteUserView
from identity.views import ListProjectView, CreateProjectView, UpdateProjectView
from identity.tests.fakes import GroupFactory

from identity.tests.fakes import FakeResource, FakeToken
from vault.tests.fakes import fake_request

import datetime


class TestListUserRole(TestCase):
    view_class = ListUserRoleView

    def setUp(self):
        self.view = ListUserView.as_view()

        self.request = fake_request(method='GET')
        self.request.user.is_superuser = True

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.LIST = 'Listou / Visualizou'
        self.mock_audit_save.VAULT_IDENTITY = 'Vault - Identity'
        self.mock_audit_save.USERS = 'Usuarios'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.user_list')
    def test_user_list_was_called_with_audit(self, mock_user_list):
        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        self.view(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.LIST, item=self.mock_audit_save.USERS, through=self.mock_audit_save.VAULT_IDENTITY, created_at=self.mock_audit_save.NOW)


class CreateUserTest(TestCase):

    def setUp(self):
        self.view = CreateUserView.as_view()

        self.request = fake_request()
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True
        self.request.user.token = FakeToken

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone.project_list',
              Mock(return_value=[FakeResource(1, 'project1')])).start()

        patch('identity.keystone.Keystone.role_list',
              Mock(return_value=[FakeResource(1, 'role1')])).start()

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.ADD = 'Cadastrou'
        self.mock_audit_save.VAULT_IDENTITY = 'Vault - Identity'
        self.mock_audit_save.USER = 'Usuario'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.user_create')
    def test_user_create_method_was_called_with_audit(self, mock):

        self.request.method = 'POST'
        post = self.request.POST.copy()
        post.update({'name': 'aaa', 'enabled': True, 'id': 1, 'project': 1,
                     'role': 1, 'password': 'aaa', 'password_confirm': 'aaa',
                     'email': 'a@a.net'})
        self.request.POST = post

        self.view(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.ADD, item=self.mock_audit_save.USER + ' - aaa', through=self.mock_audit_save.VAULT_IDENTITY, created_at=self.mock_audit_save.NOW)


class UpdateUserTest(TestCase):

    def setUp(self):
        self.view = UpdateUserView.as_view()

        self.request = fake_request()
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True
        self.request.user.token = FakeToken

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.UPDATE = 'Atualizou / Editou'
        self.mock_audit_save.VAULT_IDENTITY = 'Vault - Identity'
        self.mock_audit_save.USER = 'Usuario'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.user_update')
    def test_user_update_method_was_called_with_audit(self, mock_user_update):

        patch('identity.keystone.Keystone.project_list',
            Mock(return_value=[FakeResource(1, 'project1')])).start()

        patch('identity.keystone.Keystone.project_get',
            Mock(return_value=1)).start()

        user = FakeResource(1, 'user1')
        user.to_dict = lambda: {'name': user.name}
        user.project_id = 1

        patch('identity.keystone.Keystone.user_get',
              Mock(return_value=user)).start()

        project = FakeResource(1, 'project1')
        project.to_dict = lambda: {'name': project.name}
        patch('identity.keystone.Keystone.project_get',
              Mock(return_value=project)).start()

        self.request.method = 'POST'

        post = self.request.POST.copy()
        post.update({'id': 1, 'name': 'aaa', 'project': 1})
        self.request.POST = post

        self.view(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.UPDATE, item=self.mock_audit_save.USER + ' - user1', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.IDENTITY, created_at=self.mock_audit_save.NOW)


class DeleteUserTest(TestCase):

    def setUp(self):
        self.view = DeleteUserView.as_view()

        self.request = fake_request()
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True
        self.request.user.token = FakeToken

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.DELETE = 'Removeu'
        self.mock_audit_save.USER = 'Usuario'
        self.mock_audit_save.VAULT = 'Vault'
        self.mock_audit_save.IDENTITY = 'Identity'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.user_delete')
    def test_user_delete_method_was_called_with_audit(self, mock_user_delete):
        patch('identity.keystone.Keystone.user_get',
              Mock(return_value=FakeResource(1, 'user1'))).start()

        self.view(self.request, user_id=1)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.DELETE, item=self.mock_audit_save.USER + ' - user1', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.IDENTITY, created_at=self.mock_audit_save.NOW)


class ListProjectTest(TestCase):

    def setUp(self):
        self.view = ListProjectView.as_view()
        self.request = fake_request(method='GET')

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        patch('identity.views.Audit.save',
              Mock(return_value=None)).start()

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.LIST = 'Listou / Visualizou'
        self.mock_audit_save.VAULT = 'Vault'
        self.mock_audit_save.IDENTITY = 'Identity'
        self.mock_audit_save.VAULT_IDENTITY = 'Vault - Identity'
        self.mock_audit_save.PROJECTS = 'Projetos'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    def test_show_project_list_with_audit(self):
        patch('identity.keystone.Keystone.project_list',
              Mock(return_value=[FakeResource(1)])).start()

        self.request.user.is_authenticated = lambda: True
        self.request.user.is_superuser = True

        self.view(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.LIST, item=self.mock_audit_save.PROJECTS, through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.IDENTITY, created_at=self.mock_audit_save.NOW)


class CreateProjectTest(TestCase):

    def setUp(self):
        self.view = CreateProjectView.as_view()

        self.request = fake_request(method='GET')
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True
        self.request.user.groups = [GroupFactory(id=1)]

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.ADD = 'Cadastrou'
        self.mock_audit_save.VAULT = 'Vault'
        self.mock_audit_save.IDENTITY = 'Identity'
        self.mock_audit_save.PROJECT = 'Projeto'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    # @patch('identity.keystone.Keystone.vault_create_project')
    # def test_project_create_method_was_called_with_audit(self, mock):
    #     self.request.method = 'POST'
    #     post = self.request.POST.copy()

    #     post.update({'name': 'aaa', 'description': 'desc',
    #                 'areas': 1, 'groups': 1})
    #     self.request.POST = post

    #     self.view(self.request)

    #     self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.ADD, item=self.mock_audit_save.PROJECT + ' - aaa', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.IDENTITY, created_at=self.mock_audit_save.NOW)


class UpdateProjectTest(TestCase):

    def setUp(self):
        self.view = UpdateProjectView.as_view()

        self.request = fake_request()
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        self.post_content = {'name': 'bbb', 'description': 'desc',
                             'enabled': True, 'areas': 1, 'groups': 1}

        # MOCK FOR AUDIT and ATRIBUTES
        self.mock_audit_save = patch('identity.views.Audit').start()

        # ACTIONS / ITENS / THROUGHT
        self.mock_audit_save.UPDATE = 'Atualizou / Editou'
        self.mock_audit_save.VAULT = 'Vault'
        self.mock_audit_save.IDENTITY = 'Identity'
        self.mock_audit_save.PROJECT = 'Projeto'
        self.mock_audit_save.NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.project_update')
    def test_project_update_method_was_called_with_audit(self, mock):

        project = FakeResource(1, 'project1')
        project.to_dict = lambda: {'name': project.name}
        project.default_project_id = 1

        patch('identity.keystone.Keystone.project_get',
              Mock(return_value=project)).start()

        self.request.method = 'POST'

        post = self.request.POST.copy()
        post.update({'name': 'bbb', 'description': 'desc', 'enabled': True,
                     'areas': 1, 'groups': 1})
        self.request.POST = post

        self.view(self.request)

        self.mock_audit_save.assert_called_with(user=self.request.user.username, action=self.mock_audit_save.UPDATE, item=self.mock_audit_save.PROJECT + ' - bbb', through=self.mock_audit_save.VAULT + ' - ' + self.mock_audit_save.IDENTITY, created_at=self.mock_audit_save.NOW)
