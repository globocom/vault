# -*- coding:utf-8 -*-

from mock import Mock, patch
from unittest import TestCase

from identity.tests.fakes import FakeResource
from identity.views import ListProjectView, CreateProjectView, UpdateProjectView
from identity.tests.fakes import GroupFactory
from vault.tests.fakes import fake_request


class ListProjectTest(TestCase):

    def setUp(self):
        self.view = ListProjectView.as_view()
        self.request = fake_request(method='GET')

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        patch('identity.views.Audit.save',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_list_projects_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False
        response = self.view(self.request)
        self.assertEqual(response.status_code, 302)

    def test_show_project_list(self):
        patch('identity.keystone.Keystone.project_list',
              Mock(return_value=[FakeResource(1)])).start()

        self.request.user.is_authenticated = lambda: True
        self.request.user.is_superuser = True

        response = self.view(self.request)
        response.render()

        self.assertIn('<td>FakeResource1</td>', response.content)

    @patch('identity.keystone.Keystone.project_list')
    def test_list_project_view_exception(self, mock_project_list):
        mock_project_list.side_effect = Exception()

        self.request.user.is_authenticated = lambda: True
        self.request.user.is_superuser = True

        response = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(msgs[0].message, 'Unable to list projects')


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

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        patch('identity.views.Audit.save',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_create_project_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_validating_description_field_blank(self):
        project = FakeResource(1, 'project1')
        project.to_dict = lambda: {
            'name': project.name,
            'description': project.description
        }

        patch('identity.keystone.Keystone.project_get',
              Mock(return_value=project)).start()

        self.request.method = 'POST'

        post = self.request.POST.copy()
        post.update({
            'name': 'Project1',
            'id': 1,
            'description': ''})
        self.request.POST = post

        response = self.view(self.request)
        response.render()

        self.assertIn('This field is required', response.content)

    def test_validating_name_field_blank(self):
        project = FakeResource(1, 'project1')
        project.to_dict = lambda: {
            'name': project.name,
            'description': project.description
        }

        patch('identity.keystone.Keystone.project_get',
              Mock(return_value=project)).start()

        self.request.method = 'POST'

        post = self.request.POST.copy()
        post.update({
            'name': '',
            'id': 1,
            'description': 'description'})
        self.request.POST = post

        response = self.view(self.request)
        response.render()

        self.assertIn('This field is required', response.content)

    @patch('identity.keystone.Keystone.vault_create_project')
    def test_project_create_method_was_called(self, mock):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'name': 'aaa', 'description': 'desc',
                     'areas': 1, 'groups': 1})
        self.request.POST = post

        response = self.view(self.request)

        mock.assert_called_with('aaa', 1, 1, description='desc')

    @patch('identity.keystone.Keystone.vault_create_project')
    def test_project_create_view_exception(self, mock):
        mock.side_effect = Exception

        self.request.method = 'POST'
        post = self.request.POST.copy()
        post.update({'name': 'aaa', 'description': 'desc', 'areas': 1,
                     'groups': 1})
        self.request.POST = post

        _ = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(msgs[0].message, 'Error when create project')


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

        patch('identity.views.Audit.save',
              Mock(return_value=None)).start()

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.project_update')
    def test_project_update_method_was_called(self, mock):

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

        _ = self.view(self.request)

        mock.assert_called_with(project, enabled=True, description='desc',
                                name='bbb')
