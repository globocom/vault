# -*- coding:utf-8 -*-

from unittest import TestCase
from mock import Mock, patch

from identity.views import ListUserRoleView, AddUserRoleView, DeleteUserRoleView
from identity.tests.fakes import FakeToken, FakeResource
from vault.tests.fakes import fake_request


class BaseAjaxTestCase(TestCase):
    view_class = None

    def setUp(self):
        self.view = self.view_class.as_view()

        self.request = fake_request(method='POST')

        self.request.user.is_authenticated = lambda: True
        self.request.user.token = FakeToken
        self.request.user.is_superuser = True

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()


class TestListUserRole(BaseAjaxTestCase):
    view_class = ListUserRoleView

    def test_list_user_role_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False
        self.request.user.token = None

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_list_user_role_need_to_be_superuser(self):
        self.request.user.is_superuser = False

        response = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(msgs[0].message, 'Unauthorized')

    @patch('identity.keystone.Keystone.user_list')
    def test_list_user_role_response_content_is_json(self, mock_user_list):
        response = self.view(self.request)

        self.assertEqual(response._headers.get('content-type')[1], 'application/json')

    @patch('identity.keystone.Keystone.user_list')
    def test_user_list_was_called(self, mock_user_list):
        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        response = self.view(self.request)

        mock_user_list.assert_called_with(project_id=1)

    @patch('identity.views.ListUserRoleView.get_user_roles')
    def test_get_user_roles_was_called(self, mock_get_user_roles):
        user = FakeResource(1)
        user.username = 'User1'

        patch('identity.keystone.Keystone.user_list',
              Mock(return_value=[user])).start()

        mock_get_user_roles.return_value = []

        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        response = self.view(self.request)

        mock_get_user_roles.assert_called_with(user, 1)

    @patch('identity.views.ListUserRoleView.get_user_roles')
    def test_get_user_roles_exception(self, mock_get_user_roles):
        mock_get_user_roles.side_effect = Exception()

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestAddUserRole(BaseAjaxTestCase):
    view_class = AddUserRoleView

    def test_add_user_role_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False
        self.request.user.token = None

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_add_user_role_need_to_be_superuser(self):
        self.request.user.is_superuser = False

        response = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(msgs[0].message, 'Unauthorized')

    @patch('identity.keystone.Keystone.add_user_role')
    def test_add_user_role_response_content_is_json(self, mock_add_user_role):
        response = self.view(self.request)

        self.assertEqual(response._headers.get('content-type')[1], 'application/json')

    @patch('identity.keystone.Keystone.add_user_role')
    def test_add_user_role_was_called(self, mock_add_user_role):
        post = self.request.POST.copy()
        post.update({'project': 1, 'role': 1, 'user': 1})
        self.request.POST = post

        response = self.view(self.request)

        mock_add_user_role.assert_called_with(project=1, role=1, user=1)

    @patch('identity.keystone.Keystone.add_user_role')
    def test_add_user_role_exception(self, mock_add_user_role):
        mock_add_user_role.side_effect = Exception()

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestDeleteUserRole(BaseAjaxTestCase):
    view_class = DeleteUserRoleView

    def test_delete_user_role_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False
        self.request.user.token = None

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_delete_user_role_need_to_be_superuser(self):
        self.request.user.is_superuser = False

        response = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(msgs[0].message, 'Unauthorized')

    @patch('identity.keystone.Keystone.remove_user_role')
    def test_delete_user_role_response_content_is_json(self, mock_remove_user_role):
        response = self.view(self.request)

        self.assertEqual(response._headers.get('content-type')[1], 'application/json')

    @patch('identity.keystone.Keystone.remove_user_role')
    def test_remove_user_role_was_called(self, mock_remove_user_role):
        post = self.request.POST.copy()
        post.update({'project': 1, 'role': 1, 'user': 1})
        self.request.POST = post

        response = self.view(self.request)

        mock_remove_user_role.assert_called_with(project=1, role=1, user=1)

    @patch('identity.keystone.Keystone.remove_user_role')
    def test_remove_user_role_exception(self, mock_remove_user_role):
        mock_remove_user_role.side_effect = Exception()

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)
