# -*- coding: utf-8 -*-

import json

from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

from vault.tests.fakes import fake_request, UserFactory
from identity.tests.fakes import FakeToken
from vault.views import (DashboardView, SetProjectView, DeleteUserTeamView,
                         AddUserTeamView, ListUserTeamView, UpdateTeamsUsersView)
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group, User


class BaseTestCase(TestCase):

    def setUp(self):
        self.request = fake_request()
        self.anonymous_request = fake_request(user=False)

    def tearDown(self):
        User.objects.all().delete()
        Group.objects.all().delete()

    @classmethod
    def setUpClass(cls):
        patch('identity.keystone.v3').start()

    @classmethod
    def tearDownClass(cls):
        patch.stopall()


class DashboardTest(TestCase):

    def setUp(self):
        self.view = DashboardView.as_view()
        self.request = fake_request(method='GET')

        # does not connect to the keystone client
        patch('keystoneclient.v3.client.Client').start()

    def tearDown(self):
        patch.stopall()

    def test_dashboard_needs_authentication(self):
        req = fake_request(method='GET', user=False)
        response = self.view(req)

        self.assertEqual(response.status_code, 302)

    def test_show_dashboard(self):
        response = self.view(self.request)
        self.assertEqual(response.status_code, 200)

        response.render()
        self.assertIn(b'Dashboard', response.content)


class SetProjectTest(BaseTestCase):

    def setUp(self):
        super(SetProjectTest, self).setUp()

        self.view = SetProjectView.as_view()

    def test_set_project_needs_authentication(self):
        response = self.view(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    @patch('vault.views.switch')
    def test_set_new_project_id_to_session(self, mock_switch):
        self.assertEqual(self.request.session.get('project_id'), '1')

        response = self.view(self.request, project_id=2)
        self.assertEqual(self.request.session.get('project_id'), 2)

    @patch('vault.views.switch')
    def test_set_new_project_id_to_session_exception(self, mock_switch):
        mock_switch.side_effect = ValueError()

        self.assertEqual(self.request.session.get('project_id'), '1')

        response = self.view(self.request, project_id=2)
        self.assertEqual(self.request.session.get('project_id'), 2)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, _('Unable to change your project.'))


class TestDeleteUserTeam(BaseTestCase):
    view_class = DeleteUserTeamView

    def setUp(self):
        super(TestDeleteUserTeam, self).setUp()

        self.view = self.view_class.as_view()

        self.request.method = 'POST'

        self.group = Group(id=1, name="teamtest")
        self.group.save()

        self.user = User(id=1, username="usertest")
        self.user.save()

    def test_delete_user_and_team_flow_needs_authentication(self):
        response = self.view(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_delete_user_and_team_flow_dont_need_to_be_superuser(self):
        self.request.user.is_superuser = False

        post = self.request.POST.copy()
        post.setdefault('group', int('1'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"msg": "ok"}')

    def test_delete_user_and_team_flow_work_fine(self):
        self.request.user.is_superuser = False

        post = self.request.POST.copy()
        post.setdefault('group', int('1'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"msg": "ok"}')

    def test_delete_user_and_team_flow_fail(self):
        self.request.user.is_superuser = False

        post = self.request.POST.copy()
        post.setdefault('group', int('10'))
        post.setdefault('user', int('1'))

        self.request.POST = post

        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestListUserTeam(BaseTestCase):
    view_class = ListUserTeamView

    def setUp(self):
        super(TestListUserTeam, self).setUp()

        self.view = self.view_class.as_view()

        self.request.method = 'POST'

        self.group = Group(id=1, name="teamtest")
        self.group.save()

        self.user = User(id=1, username="usertest")
        self.user.save()

    def test_list_users_teams_flow_needs_authentication(self):
        req = fake_request(user=False)
        response = self.view(req)

        self.assertEqual(response.status_code, 302)

    def test_list_users_teams_flow_dont_need_to_be_superuser(self):
        self.request.user.is_superuser = False
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)

    def test_list_users_teams_flow_work_fine(self):
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason_phrase, 'OK')

    @patch('django.contrib.auth.models.Group.objects.get')
    def test_list_users_teams_flow_fail(self, mock_get):
        mock_get.return_value = None
        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)


class TestAddUserTeam(BaseTestCase):
    view_class = AddUserTeamView

    def setUp(self):
        super(TestAddUserTeam, self).setUp()

        self.view = self.view_class.as_view()

        self.request.method = 'POST'
        self.anonymous_request.method = 'POST'

        self.group = Group(id=1, name="teamtest")
        self.group.save()

        self.user = User(id=1, username="usertest")
        self.user.save()

    def test_add_user_and_team_flow_needs_authentication(self):
        response = self.view(self.anonymous_request)

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

    def test_add_user_and_team_flow_from_user_fail(self):
        req = fake_request(method='POST')
        req.user.is_superuser = False

        post = req.POST.copy()
        post.setdefault('group', int('10'))
        post.setdefault('user', int('1'))

        req.POST = post

        response = self.view(req)

        self.assertEqual(response.status_code, 500)


class UpdateTeamsUsersTest(BaseTestCase):

    def setUp(self):
        super(UpdateTeamsUsersTest, self).setUp()

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

        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80',
            'HTTP_HOST': 'localhost'
        })

        # Silent log
        mock_log = patch('vault.views.log').start()

        # does not connect to the keystone client
        # patch('keystoneclient.v2_0.client.Client').start()

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

    def test_manage_users_teams_flow_needs_authentication(self):
        response = self.view(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    @patch('vault.templatetags.vault_tags.requests.get')
    def test_manage_users_teams_flow_ensure_user_list_was_filled_up(self, mock_response):
        mock_response.return_value = MagicMock(status_code=200, content=json.dumps(self.roles))
        response = self.view(self.request)
        response.render()

        self.assertIn('<option value="2">usertest-2</option>', response.content.decode('utf-8'))

    @patch('vault.templatetags.vault_tags.requests.get')
    def test_manage_users_teams_flow_ensure_group_list_was_filled_up(self, mock_response):
        mock_response.return_value = MagicMock(status_code=200, content=json.dumps(self.roles))
        response = self.view(self.request)
        response.render()
        group = self.request.user.groups.first()

        self.assertIn('<option value="{}">{}'.format(group.id, group.name),
                      response.content.decode('utf-8'))

    def test_manage_users_teams_flow_for_a_user_not_superuser_work_fine(self):
        self.request.user.is_superuser = False
        response = self.view(self.request)

        self.assertEqual(response.status_code, 200)

    @patch('django.contrib.auth.models.Group.objects.all')
    def test_manage_users_teams_fail_to_get_user_group(self, mock_all):
        mock_all.return_value = None
        response = self.view(self.request)

        self.assertEqual(response.status_code, 500)
