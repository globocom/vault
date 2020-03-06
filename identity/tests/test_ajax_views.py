# -*- coding:utf-8 -*-

import json

from unittest import TestCase
from unittest.mock import patch

from identity.views import (
    ListUserRoleView, AddUserRoleView, DeleteUserRoleView)
from identity.tests.fakes import FakeToken, FakeResource
from vault.tests.fakes import fake_request, UserFactory


class BaseAjaxTestCase(TestCase):
    view_class = None

    def setUp(self):
        self.view = self.view_class.as_view()
        self.request = fake_request(method='POST')

        self.request.user.token = FakeToken
        self.request.user.is_superuser = True

        patch('identity.keystone.Keystone._create_keystone_connection').start()
        patch('identity.views.log').start()

    def tearDown(self):
        patch.stopall()


class TestListUserRole(BaseAjaxTestCase):
    view_class = ListUserRoleView

    def setUp(self):
        super(TestListUserRole, self).setUp()
        self.mock_user_list = patch(
            'identity.keystone.Keystone.user_list').start()

    def test_list_user_role_needs_authentication(self):
        req = fake_request(method='POST', user=False)
        response = self.view(req)

        self.assertEqual(response.status_code, 302)

    def test_list_user_role_need_to_be_superuser(self):
        self.request.user.is_superuser = False

        response = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(msgs[0].message, 'Unauthorized')

    def test_list_user_role_response_content_is_json(self):
        response = self.view(self.request)
        self.assertEqual(response._headers.get(
            'content-type')[1], 'application/json')

    @patch('identity.views.ListUserRoleView.get_user_roles')
    def test_list_user_role_return_sorted_users(self, mock_get_user_roles):
        user1 = FakeResource(1)
        user1.name = 'ZZZ'

        user2 = FakeResource(2)
        user2.name = 'BBBB'

        user3 = FakeResource(3)
        user3.name = 'LLLL'

        self.mock_user_list.return_value = [user1, user2, user3]
        mock_get_user_roles.return_value = []

        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        response = self.view(self.request)

        computed = json.loads(response.content)
        computed_names = [x.get('username') for x in computed.get('users')]
        expected = sorted([user1.name, user2.name, user3.name])

        self.assertEqual(computed_names, expected)

    def test_user_list_was_called(self):
        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        self.view(self.request)

        self.mock_user_list.assert_called_with(project_id=1)

    @patch('identity.views.ListUserRoleView.get_user_roles')
    def test_get_user_roles_was_called(self, mock_get_user_roles):
        user = FakeResource(1)
        user.username = 'User1'

        self.mock_user_list.return_value = [user]
        mock_get_user_roles.return_value = []

        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        self.view(self.request)

        mock_get_user_roles.assert_called_with(user, 1)

    @patch('identity.views.ListUserRoleView.get_user_roles')
    def test_get_user_roles_exception(self, mock_get_user_roles):
        mock_get_user_roles.side_effect = Exception()
        mock_get_user_roles.return_value = []

        user = FakeResource(1)
        user.username = 'User1'

        self.mock_user_list.return_value = [user]

        post = self.request.POST.copy()
        post.update({'project': 1})
        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestAddUserRole(BaseAjaxTestCase):
    view_class = AddUserRoleView

    def test_add_user_role_needs_authentication(self):
        req = fake_request(method='POST', user=False)
        self.request.user.token = None
        response = self.view(req)

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

        self.assertEqual(response._headers.get(
            'content-type')[1], 'application/json')

    @patch('identity.keystone.Keystone.add_user_role')
    def test_add_user_role_was_called(self, mock_add_user_role):
        post = self.request.POST.copy()
        post.update({'project': 1, 'role': 1, 'user': 1})
        self.request.POST = post

        self.view(self.request)

        mock_add_user_role.assert_called_with(project=1, role=1, user=1)

    @patch('identity.keystone.Keystone.add_user_role')
    def test_add_user_role_exception(self, mock_add_user_role):
        mock_add_user_role.side_effect = Exception()

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestDeleteUserRole(BaseAjaxTestCase):
    view_class = DeleteUserRoleView

    def test_delete_user_role_needs_authentication(self):
        req = fake_request(method='POST', user=False)
        self.request.user.token = None

        response = self.view(req)

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

        self.assertEqual(response._headers.get(
            'content-type')[1], 'application/json')

    @patch('identity.keystone.Keystone.remove_user_role')
    def test_remove_user_role_was_called(self, mock_remove_user_role):
        post = self.request.POST.copy()
        post.update({'project': 1, 'role': 1, 'user': 1})
        self.request.POST = post

        self.view(self.request)

        mock_remove_user_role.assert_called_with(project=1, role=1, user=1)

    @patch('identity.keystone.Keystone.remove_user_role')
    def test_remove_user_role_exception(self, mock_remove_user_role):
        mock_remove_user_role.side_effect = Exception()

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)
