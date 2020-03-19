# -*- coding:utf-8 -*-

from unittest.mock import Mock, patch
from unittest import TestCase

from django.utils.translation import gettext as _

from keystoneclient import exceptions

from identity import views
from identity.tests.fakes import FakeResource

from vault.tests.fakes import fake_request


class ListProjectTest(TestCase):

    def setUp(self):
        patch('identity.keystone.Keystone._create_keystone_connection').start()
        patch('identity.views.log').start()

        self.view = views.ListProjectView.as_view()
        self.request = fake_request(method='GET')

    def tearDown(self):
        patch.stopall()

    def test_list_projects_needs_authentication(self):
        req = fake_request(method='GET', user=False)
        response = self.view(req)

        self.assertEqual(response.status_code, 302)

    def test_show_project_list(self):
        """
        We only check if the project_list view is being called with the
        right list of projects on the context.
        """
        fake_project = FakeResource(1)

        # This mocks is faking keystone retrieving a defined list of
        # projects
        patch('identity.views.Keystone.project_list',
              Mock(return_value=[fake_project])).start()

        render_mock = patch(
            'identity.views.ListProjectView.render_to_response').start()

        response = self.view(self.request)

        render_args = render_mock.call_args[0][0]
        computed = render_args['projects'][0]

        self.assertEqual(computed, fake_project.to_dict())

    @patch('identity.keystone.Keystone.project_list')
    def test_list_project_view_exception(self, mock_project_list):
        mock_project_list.side_effect = Exception()

        response = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(msgs[0].message, _('Unable to list projects'))


class CreateProjectTest(TestCase):

    def setUp(self):
        patch('identity.keystone.Keystone._create_keystone_connection').start()
        patch('identity.views.actionlog.log').start()
        patch('identity.views.log').start()
        patch('identity.views.CreateProjectView.get_context_data').start()

        self.form = patch('identity.views.ProjectForm').start()
        self.view = views.CreateProjectView.as_view()

        self.request = fake_request(method='POST')

        self.group = self.request.user.groups.first()

        post = self.request.POST.copy()
        post.update({
            'name': 'project-teste',
            'description': 'desc',
            'enabled': True,
            'group': self.group.id
        })
        self.request.POST = post

    def test_create_project_needs_authentication(self):
        req = fake_request(method='POST', user=False)
        response = self.view(req)

        self.assertEqual(response.status_code, 302)

    @patch('identity.keystone.Keystone.vault_project_create')
    def test_invove_vault_project_create_when_request_is_valid(self, mock):
        mock.return_value = {
            'status': True,
            'user': FakeResource(),
            'project': FakeResource()
        }

        # Fake the validation of the form
        self.form.return_value.is_valid.return_value = True
        response = self.view(self.request)
        group_id = self.group.id

        mock.assert_called_with('project-teste', group_id,
                                created_by='vault', description='desc',
                                team_owner_id=group_id, first_team_id=group_id)

    @patch('identity.keystone.Keystone.vault_project_create')
    def test_dont_invove_vault_project_create_when_request_is_valid(self, mock):

        # Fake the validation of the form
        self.form.return_value.is_valid.return_value = False
        response = self.view(self.request)

        self.assertFalse(mock.called)


class CreateProjectSuccessTest(TestCase):

    def setUp(self):
        self.view = views.CreateProjectSuccessView.as_view()
        self.request = fake_request(method='GET')
        self.mock_keystone_conn = patch('identity.keystone.Keystone._create_keystone_connection').start()

    @patch('identity.views.Keystone.get_endpoints')
    @patch('identity.views.CreateProjectSuccessView.render_to_response')
    def test_render_success_create_page(self, mock_render, mock_get_endpoints):

        os_endpoints = {
            u'adminURL': u'https://adminURL/storage',
            u'publicURL': u'https://publicURL/storage',
            u'internalURL': u'https://internalURL/storage'}

        bs_enpoints = {
            u'adminURL': u'https://adminURL/faas',
            u'publicURL': u'https://publicURL/faas',
            u'internalURL': u'https://internalURL/faas'}

        mock_get_endpoints.return_value = {
            u'object_store': os_endpoints,
            u'block_storage': bs_enpoints
        }

        project_create_result = {
            'user_name': 'fake_user',
            'project_name': 'fake_project',
            'user_password': 'secret'
        }

        self.request.session['project_info'] = project_create_result
        _ = self.view(self.request)

        called_args, _ = mock_render.call_args
        computed_project_info = called_args[0]['project_info']

        computed_os_endpoints = computed_project_info['endpoints']['object_store']
        self.assertEqual(os_endpoints, computed_os_endpoints)

        computed_bs_enpoints = computed_project_info['endpoints']['block_storage']
        self.assertEqual(bs_enpoints, computed_bs_enpoints)

        self.assertEqual('fake_user', computed_project_info['user_name'])
        self.assertEqual('fake_project', computed_project_info['project_name'])
        self.assertEqual('secret', computed_project_info['user_password'])


class UpdateProjectTestTest(TestCase):
    """
    Tests for UpdateProjectView

    - Verify if the form is invalid, won't invoke
      keystone.vault_update_project_tsuru

    - Verify if the form is valid, what arguments are being used
    """

    def setUp(self):
        patch('identity.keystone.Keystone._create_keystone_connection').start()
        patch('identity.views.actionlog.log').start()
        patch('identity.views.log').start()

        patch('identity.views.Keystone.project_get',
              return_value=FakeResource(1, 'fake_resource')).start()

        self.mock_get_context_data = patch(
            'identity.views.UpdateProjectView.get_context_data').start()

        # Mock form validation. It's mocked as a invalid form.
        form = patch('identity.views.ProjectForm').start()
        self.form_is_valid = form.return_value.is_valid

        self.view = views.UpdateProjectView.as_view()

        self.request = fake_request(method='POST')

        post = self.request.POST.copy()
        post.update({
            'name': 'update_teste',
            'description': 'update desc',
            'group': 1,
            'enabled': 'False'})
        self.request.POST = post

    @patch('identity.keystone.Keystone.vault_project_update')
    def test_invalid_form_dont_invoke_vault_project_update(self, mock):
        # Inverting this return value must fail the test
        self.form_is_valid.return_value = False
        _ = self.view(self.request)

        mock.assert_not_called()
        self.assertTrue(self.mock_get_context_data.called)

    @patch('identity.keystone.Keystone.vault_project_update')
    def test_valid_form_invoke_vault_project_update(self, mock):
        # Inverting this return value must fail the test
        self.form_is_valid.return_value = True
        _ = self.view(self.request)

        group_id = self.request.POST.get('group')
        mock.assert_called_with(
            1,
            'fake_resource',
            group_id,
            description=self.request.POST.get('description'),
            enabled=False,
            team_owner_id=group_id)


class DeleteProjectTest(TestCase):
    """
    Tests for DeleteProjectView

    - Verify if the form is invalid, won't invoke
      keystone.vault_delete_project

    - Verify if the form is valid, but the credentials are invalid,
      won't invoke keystone.vault_delete_project

    - Verify if the form and the credentials are valid, what arguments
      are being used to invoke keystone.vault_delete_project
    """

    def setUp(self):
        patch('identity.keystone.Keystone._create_keystone_connection').start()
        patch('identity.views.actionlog.log').start()
        patch('identity.views.log').start()
        patch('identity.views.DeleteProjectView.get_context_data').start()

        self.form = patch('identity.views.DeleteProjectConfirm').start()
        self.view = views.DeleteProjectView.as_view()
        self.request = fake_request(method='GET')

    def tearDown(self):
        patch.stopall()

    def test_delete_project_needs_authentication(self):
        req = fake_request(method='GET', user=False)
        response = self.view(req)

        self.assertEqual(response.status_code, 302)

    def test_get_request_invoke_render_with_form_object(self):
        """
        It tests if the view render method is invoked passing the proper
        form object
        """

        mock_render = patch(
            'identity.views.DeleteProjectView.get_context_data').start()

        fake_resource = FakeResource()
        self.form.return_value = fake_resource
        _ = self.view(self.request)

        computed_form = mock_render.call_args[1].get('form')
        self.assertEqual(fake_resource, computed_form)

    def test_post_invalid_form(self):
        mock_delete = patch(
            'identity.keystone.Keystone.vault_project_delete').start()

        mock_render = patch(
            'identity.views.DeleteProjectView.render_to_response').start()

        self.request.method = 'POST'

        self.form.return_value.is_valid.return_value = False

        _ = self.view(self.request)

        self.assertEqual(1, mock_render.call_count)
        mock_delete.assert_not_called()

    @patch('identity.views.Keystone')
    def test_get_delete_url_return_200(self, mock_keystone):
        self.request.method = 'GET'
        response = self.view(self.request)

        self.assertEqual(200, response.status_code)

    @patch('identity.views.Keystone')
    def test_delete_project_connect_with_username_and_password_passed_by_form(self, mock_keystone):
        self.view(self.request, project_id='12345abcef')

        mock_keystone.asser_called_with(
            self.request, username='teste_user', password='secret')
