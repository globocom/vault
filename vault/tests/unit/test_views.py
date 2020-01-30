# -*- coding: utf-8 -*-

import json

from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from vault.tests.fakes import fake_request
from identity.tests.fakes import FakeToken
from vault.views import (SetProjectView, DeleteUserTeamView, AddUserTeamView,
    ListUserTeamView, UpdateTeamsUsersView)
from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group, User


class SetProjectTest(TestCase):

    def setUp(self):
        self.view = SetProjectView.as_view()
        self.request = fake_request(method='GET')
        self.request.user.is_authenticated = False

    def tearDown(self):
        patch.stopall()

    def test_set_project_needs_authentication(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 302)

    @patch('vault.views.switch')
    def test_set_new_project_id_to_session(self, mock_switch):
        self.request.user.is_authenticated = True
        self.assertEqual(self.request.session.get('project_id'), '1')

        response = self.view(self.request, project_id=2)
        self.assertEqual(self.request.session.get('project_id'), 2)

    @patch('vault.views.switch')
    def test_set_new_project_id_to_session_exception(self, mock_switch):
        self.request.user.is_authenticated = True
        mock_switch.side_effect = ValueError()

        self.assertEqual(self.request.session.get('project_id'), '1')

        response = self.view(self.request, project_id=2)
        self.assertEqual(self.request.session.get('project_id'), 2)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, _('Unable to change your project.'))


class TestDeleteUserTeam(TestCase):
    view_class = DeleteUserTeamView

    def setUp(self):
        self.view = self.view_class.as_view()

        self.request = fake_request(method='POST')

        self.request.user.is_authenticated = True

        self.group = Group(id=1, name="teamtest")
        self.group.save()

        self.user = User(id=1, username="usertest")
        self.user.save()

    def tearDown(self):
        self.group.delete()
        self.user.delete()

    def test_delete_user_and_team_flow_needs_authentication(self):
        self.request.user.is_authenticated = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_delete_user_and_team_flow_dont_need_to_be_superuser(self):
        self.request.user.is_superuser = False
        self.request.user.is_authenticated = True

        post = self.request.POST.copy()
        post.setdefault('group', int('1'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"msg": "ok"}')

    def test_delete_user_and_team_flow_work_fine(self):
        self.request.user.is_superuser = False
        self.request.user.is_authenticated = True

        post = self.request.POST.copy()
        post.setdefault('group', int('1'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"msg": "ok"}')

    def test_delete_user_and_team_flow_fail(self):
        self.request.user.is_superuser = False
        self.request.user.is_authenticated = True

        post = self.request.POST.copy()
        post.setdefault('group', int('10'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestListUserTeam(TestCase):
    view_class = ListUserTeamView

    def setUp(self):
        self.view = self.view_class.as_view()

        self.request = fake_request(method='POST')

        self.request.user.is_authenticated = True

        self.group = Group(id=1, name="teamtest")
        self.group.save()

        self.user = User(id=1, username="usertest")
        self.user.save()

    def tearDown(self):
        self.group.delete()
        self.user.delete()

    def test_list_users_teams_flow_needs_authentication(self):
        self.request.user.is_authenticated = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_list_users_teams_flow_dont_need_to_be_superuser(self):
        self.request.user.is_superuser = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)

    def test_list_users_teams_flow_work_fine(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason_phrase, 'OK')

    def test_list_users_teams_flow_fail(self):
        self.request.user.groups.all = None

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestAddUserTeam(TestCase):
    view_class = AddUserTeamView

    def setUp(self):
        self.view = self.view_class.as_view()

        self.request = fake_request(method='POST')

        self.request.user.is_authenticated = True

        self.group = Group(id=1, name="teamtest")
        self.group.save()

        self.user = User(id=1, username="usertest")
        self.user.save()

    def tearDown(self):
        self.group.delete()
        self.user.delete()

    def test_add_user_and_team_flow_needs_authentication(self):
        self.request.user.is_authenticated = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_add_user_and_team_flow_from_user_not_superuser_work_fine(self):
        self.request.user.is_superuser = False

        post = self.request.POST.copy()
        post.setdefault('group', int('1'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)

    def test_add_user_and_team_flow_from_user_already_registered(self):
        self.request.user.is_superuser = False

        post = self.request.POST.copy()
        post.setdefault('group', int('1'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"msg": "ok"}')

        response2 = self.view(self.request)

        self.assertEqual(response2.status_code, 500)

    def test_add_user_and_team_flow_redirect_for_user_not_logged(self):
        self.request.user.is_authenticated = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_add_user_and_team_flow_from_user_fail(self):
        self.request.user.is_superuser = False
        self.request.user.is_authenticated = True

        post = self.request.POST.copy()
        post.setdefault('group', int('10'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class UpdateTeamsUsersTest(TestCase):

    def setUp(self):
        self.view = UpdateTeamsUsersView.as_view()

        self.roles = {
            "roles": {
                "driver_processado": [
                    {"1751": "qa2"},
                    {"11": "Storm"}
                ],
                "sheets": [
                    {"1754": "Financeiro"},
                    {"11": "Storm"}
                ],
                "reports": [
                    {"11": "Storm"}
                ]
            }
        }

        self.request = fake_request()
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80',
            'HTTP_HOST': 'localhost'
        })
        self.request.user.is_superuser = False
        self.request.user.is_authenticated = True

        # Silent log
        mock_log = patch('vault.views.log').start()

        # does not connect to the keystone client
        patch('keystoneclient.v2_0.client.Client').start()

        group = Group(id=1, name="teamtest")
        group.save()

        # Usuario do time "teamtest"
        user = User(id=1, username="usertest-1")
        user.save()
        user.groups.add(group)
        user.save()

        # Usuario sem time, para ser adicionado ao time "teamtest"
        user = User(id=2, username="usertest-2")
        user.save()

    def tearDown(self):
        # self.group.delete()
        # self.user.delete()
        user = User(id=1)
        user.delete()

        user = User(id=2)
        user.delete()

        group = Group(id=1)
        group.delete()

    def test_manage_users_teams_flow_needs_authentication(self):
        self.request.user.is_authenticated = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    @patch('vault.templatetags.vault_tags.requests.get')
    def test_manage_users_teams_flow_ensure_user_list_was_filled_up(self, mock_response):
        mock_response.return_value = MagicMock(status_code=200, content=json.dumps(self.roles))
        response = self.view(self.request)
        response.render()

        self.assertIn(b'<option value="2">usertest-2</option>', response.content)

    @patch('vault.templatetags.vault_tags.requests.get')
    def test_manage_users_teams_flow_ensure_group_list_was_filled_up(self, mock_response):
        mock_response.return_value = MagicMock(status_code=200, content=json.dumps(self.roles))
        response = self.view(self.request)
        response.render()

        self.assertIn(b'<option value="1">Group', response.content)

    def test_manage_users_teams_flow_for_a_user_not_superuser_work_fine(self):
        self.request.user.is_superuser = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)

    def test_manage_users_teams_flow_for_a_user_redirect_for_user_not_logged(self):
        self.request.user.is_authenticated = False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_manage_users_teams_fail_to_get_user_group(self):
        self.request.user.groups.all = Mock(side_effect=Exception)
        response = self.view(self.request)
        self.assertEqual(response.status_code, 500)
