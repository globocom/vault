# -*- coding:utf-8 -*-

from mock import Mock, patch
from unittest import TestCase

from keystoneclient.openstack.common.apiclient import exceptions

from identity import views
from identity.tests.fakes import FakeResource
from identity.tests.fakes import AreaFactory, AreaProjectsFactory, \
    GroupProjectsFactory
from vault.tests.fakes import fake_request
from django.utils.translation import ugettext as _


class ListProjectTest(TestCase):

    def setUp(self):
        self.view = views.ListProjectView.as_view()
        self.request = fake_request(method='GET')

        self.mock_keystone_is_allowed = patch('identity.keystone.Keystone._is_allowed_to_connect').start()

        self.mock_area = patch('identity.forms.Area.objects.all').start()
        self.mock_area.return_value = [AreaFactory(id=1)]

        patch('identity.keystone.Keystone._keystone_conn',
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
        self.assertEqual(msgs[0].message, _('Unable to list projects'))


class CreateProjectTest(TestCase):

    def setUp(self):
        self.view = views.CreateProjectView.as_view()

        self.request = fake_request(method='GET')
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        self.mock_keystone_is_allowed = patch('identity.keystone.Keystone._is_allowed_to_connect').start()

        self.mock_keystone_find_user = patch('identity.keystone.Keystone.return_find_u_user').start()
        # Retorna objeto usuário similar ao do request
        self.mock_keystone_find_user.return_value = fake_request(method='GET').user

        self.mock_area = patch('identity.forms.Area.objects.all').start()
        self.mock_area.return_value = [AreaFactory(id=1)]

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_create_project_needs_authentication(self):
        self.request.user.is_authenticated = lambda: False

        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)

    @patch('identity.views.AreaProjects.objects.get')
    @patch('identity.views.GroupProjects.objects.get')
    def test_validating_description_field_blank(self, mock_gp, mock_ap):

        mock_gp.return_value = GroupProjectsFactory.build(group_id=1, project_id=1)
        mock_ap.return_value = AreaProjectsFactory.build(area_id=1, project_id=1)

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

        self.assertIn(_('This field is required'), response.content.decode('UTF-8'))

    @patch('identity.views.AreaProjects.objects.get')
    @patch('identity.views.GroupProjects.objects.get')
    def test_validating_name_field_blank(self, mock_gp, mock_ap):

        mock_gp.return_value = GroupProjectsFactory.build(group_id=1, project_id=1)
        mock_ap.return_value = AreaProjectsFactory.build(area_id=1, project_id=1)

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

        self.assertIn(_('This field is required'), response.content.decode('UTF-8'))

    @patch('identity.views.AreaProjects.objects.get')
    @patch('identity.views.GroupProjects.objects.get')
    def test_validating_description_field_whitespaces(self, mock_gp, mock_ap):

        mock_gp.return_value = GroupProjectsFactory.build(group_id=1, project_id=1)
        mock_ap.return_value = AreaProjectsFactory.build(area_id=1, project_id=1)

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
            'description': '   '})
        self.request.POST = post
        response = self.view(self.request)
        response.render()

        self.assertIn(_('Project description cannot be empty.'), response.content.decode('UTF-8'))

    @patch('identity.views.AreaProjects.objects.get')
    @patch('identity.views.GroupProjects.objects.get')
    def test_validating_name_field_non_alphanumeric(self, mock_gp, mock_ap):

        mock_gp.return_value = GroupProjectsFactory.build(group_id=1, project_id=1)
        mock_ap.return_value = AreaProjectsFactory.build(area_id=1, project_id=1)

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
            'name': 'valor inválido',
            'id': 1,
            'description': 'description'})
        self.request.POST = post

        response = self.view(self.request)
        response.render()

        self.assertIn(_('Project Name must be an alphanumeric.'), response.content.decode('UTF-8'))

    @patch('identity.keystone.Keystone.vault_create_project')
    def test_project_create_method_was_called(self, mock):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'name': 'aaa', 'description': 'desc',
                     'areas': 1, 'groups': 1})
        self.request.POST = post

        _ = self.view(self.request)

        mock.assert_called_with('aaa', 1, 1, description='desc')

    @patch('identity.keystone.Keystone.vault_create_project')
    def test_project_create_return_status_false(self, mock):
        mock.return_value = {
            'status': False,
            'reason': 'Blah'
        }

        self.request.method = 'POST'
        post = self.request.POST.copy()
        post.update({'name': 'aaa', 'description': 'desc', 'areas': 1,
                     'groups': 1})
        self.request.POST = post

        _ = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(msgs[0].message, 'Blah')

    @patch('identity.keystone.Keystone.project_create')
    def test_project_create_conflict_on_create_project(self, mock):

        mock.side_effect = exceptions.Conflict

        self.request.method = 'POST'
        post = self.request.POST.copy()
        post.update({'name': 'aaa', 'description': 'desc', 'areas': 1,
                     'groups': 1})
        self.request.POST = post

        _ = self.view(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertGreater(len(msgs), 0)
        self.assertEqual(msgs[0].message, 'Duplicated project name.')

    def test_superuser_creating_project_at_admin_must_see_box_role(self):
        """
        Tela admin de criacao de projeto deve exibir o box de roles quando
        acessado por um superusuario (teoricamente somente o superusuario vera
        esta tela)
        """
        self.request.user.is_authenticated = lambda: True
        self.request.path = '/admin/project/add'
        response = self.view(self.request)
        response.render()

        self.assertTrue(response.context_data.get('show_roles'))
        self.assertIn('add-user-role', response.content)

    def test_superuser_creating_project_must_NOT_see_box_role(self):
        """
        Tela padrao de criacao de projeto deve ser igual tanto para usuario como
        superusuario, nao exibindo o box de roles
        """
        self.request.path = '/project/add'
        response = self.view(self.request)
        response.render()

        self.assertFalse(response.context_data.get('show_roles'))
        self.assertNotIn('add-user-role', response.content)

    def test_common_user_creating_project_must_NOT_see_box_role(self):
        """
        Tela padrao de criacao de projeto deve ser igual tanto para usuario como
        superusuario, nao exibindo o box de roles
        """
        self.request.user.is_superuser = False
        self.request.path = '/project/add'

        response = self.view(self.request)
        response.render()

        self.assertFalse(response.context_data.get('show_roles'))
        self.assertNotIn('add-user-role', response.content)


class CreateProjectSuccessTest(TestCase):

    def setUp(self):
        self.view = views.CreateProjectSuccessView.as_view()

        self.request = fake_request(method='GET')
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True

        self.mock_keystone_conn = patch('identity.keystone.Keystone._keystone_conn').start()
        self.mock_is_allowed_to_connect = patch('identity.keystone.Keystone._is_allowed_to_connect').start()

    @patch('identity.keystone.Keystone.get_endpoints')
    def test_render_success_create_page(self, mock_get_endpoints):

        mock_get_endpoints.return_value = {
            'adminURL': 'https://adminURL',
            'publicURL': 'https://publicURL',
            'internalURL': 'https://internalURL',
        }

        project_create_result = {
            'user_name': 'fake_user',
            'project_name': 'fake_project',
            'user_password': 'secret'
        }

        self.request.session['project_info'] = project_create_result

        response = self.view(self.request)
        response.render()

        self.assertEqual(response.status_code, 200)
        self.assertIn(_('Project Created'), response.content.decode('UTF-8'))

        context_data = response.context_data

        # Verifica se o retorno de criacao do project esta na sessao
        self.assertEqual(context_data['project_info'], project_create_result)

        user_name = context_data['project_info'].get('user_name')
        password = context_data['project_info'].get('user_password')
        auth_url = context_data['project_info'].get('auth_url')
        endpoints = context_data['project_info'].get('endpoints')

        self.assertIn(user_name, response.content)
        self.assertIn(password, response.content)
        self.assertIn(auth_url, response.content)

        self.assertIn(endpoints.get('adminURL'), response.content)
        self.assertIn(endpoints.get('publicURL'), response.content)
        self.assertIn(endpoints.get('internalURL'), response.content)


class UpdateProjectTest(TestCase):

    def setUp(self):
        self.view = views.UpdateProjectView.as_view()

        self.request = fake_request()
        self.request.META.update({
            'SERVER_NAME': 'globo.com',
            'SERVER_PORT': '80'
        })
        self.request.user.is_superuser = True
        self.request.user.is_authenticated = lambda: True

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        self.mock_keystone_is_allowed = patch('identity.keystone.Keystone._is_allowed_to_connect').start()
        self.mock_area = patch('identity.forms.Area.objects.all').start()
        self.mock_area.return_value = [AreaFactory(id=1)]

        self.mock_keystone_find_user = patch('identity.keystone.Keystone.return_find_u_user').start()
        # Retorna objeto usuário similar ao do request
        self.mock_keystone_find_user.return_value = fake_request(method='GET').user

        self.mock_users_list = patch('identity.keystone.Keystone.user_list').start()
        self.mock_users_list.return_value = [fake_request(method='GET').user]

        patch('identity.keystone.Keystone._keystone_conn',
              Mock(return_value=None)).start()

        self.post_content = {'name': 'bbb', 'description': 'desc',
                             'enabled': True, 'areas': 1, 'groups': 1}

    def tearDown(self):
        patch.stopall()

    @patch('identity.keystone.Keystone.vault_update_project')
    def test_vault_update_project_method_was_called(self, mock):

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

        mock.assert_called_with(project.id, project.name, 1, 1,
                                description='desc', enabled=True)

    @patch('identity.views.AreaProjects.objects.get')
    @patch('identity.views.GroupProjects.objects.get')
    def test_update_validating_name_field_blank(self, mock_gp, mock_ap):

        mock_gp.return_value = GroupProjectsFactory.build(group_id=1, project_id=1)
        mock_ap.return_value = AreaProjectsFactory.build(area_id=1, project_id=1)

        project = FakeResource(1, 'project1')
        project.to_dict = lambda: {'name': project.name}
        project.default_project_id = 1

        patch('identity.keystone.Keystone.project_get',
              Mock(return_value=project)).start()

        self.request.method = 'POST'

        post = self.request.POST.copy()
        post.update({
            'name': '',
            'id': 1,
            'description': 'description',
            'groups': 1,
            'areas': 1})

        self.request.POST = post

        response = self.view(self.request)
        response.render()

        self.assertIn(_('This field is required'), response.content.decode('UTF-8'))

    @patch('identity.views.GroupProjects.objects.get')
    @patch('identity.views.AreaProjects.objects.get')
    def test_initial_data_loaded(self, mock_ap, mock_gp):
        group_id = 123
        area_id = 456

        mock_gp.return_value = GroupProjectsFactory(id=1, group_id=group_id)
        mock_ap.return_value = AreaProjectsFactory(id=2, area_id=area_id)

        project = FakeResource(1, 'project1')
        project.default_project_id = 1
        project.description = 'description'
        project.to_dict = lambda: {'name': project.name,
                                   'description': project.description}

        patch('identity.keystone.Keystone.project_get',
              Mock(return_value=project)).start()

        response = self.view(self.request, project_id='project_id')

        computed_form = response.context_data['form']

        self.assertEqual(computed_form.initial['name'], project.name)
        self.assertEqual(computed_form.initial['description'], project.description)
        self.assertEqual(computed_form.initial['groups'], group_id)
        self.assertEqual(computed_form.initial['areas'], area_id)


class DeleteProjectTest(TestCase):

    def setUp(self):
        self.view = views.DeleteProjectView.as_view()
        self.request = fake_request()
        self.request.method = 'POST'
        self.request.user.is_authenticated = lambda: True
        post = self.request.POST.copy()
        post.update({
            'user': 'teste_user',
            'password': 'secret'})

        self.request.POST = post

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()
        #
        # kwargs = {
        #     'remote_addr': request.environ.get('REMOTE_ADDR', ''),
        #     'auth_url': getattr(settings, 'KEYSTONE_URL'),
        #     'insecure': True,
        #     'tenant_name': self.tenant_name,
        #     'username': self.username,
        #     'password': self.password,
        #     'timeout': 3,
        # }

        fake_project = FakeResource(n='abcdefg', name='fake_project')
        fake_project.description = 'desc do fake'

        # Mocking Keystone class used on vault views mixin
        self.mock_vault_keystone = patch('vault.views.Keystone').start()

        self.mock_project_get = patch('identity.keystone.Keystone.project_get').start()
        self.mock_project_get.return_value = fake_project

    def tearDown(self):
        patch.stopall()

    def test_get_delete_url_return_200(self):
        self.request.method = 'GET'
        response = self.view(self.request)
        self.assertEqual(200, response.status_code)

    @patch('identity.views.Keystone')
    def test_delete_project_connect_with_username_and_password_passed_by_form(self, mock_keystone):
        _ = self.view(self.request, project_id='12345abcef')

        mock_keystone.asser_called_with(self.request, username='teste_user', password='secret')

    @patch('identity.views.Keystone')
    @patch('identity.views.delete_swift_account')
    def test_call_delete_swift_account_with_proper_storage_url_and_auth_token(self, mock_delete, mock_keystone):
        """
        This test checks if delete_swift_account will be called with the
        project_id storage_url and the "admin" auth_token. They are from
        different keystone instances
        """
        mock_keystone.return_value.get_endpoints.return_value = {
            'adminURL': 'http://api.end.point'
        }

        self.mock_vault_keystone.return_value.conn.auth_token = 'auth_token'

        _ = self.view(self.request, project_id='12345abcef')

        mock_delete.assert_called_with('http://api.end.point', 'auth_token')

    @patch('identity.views.Keystone')
    def test_vault_delete_project_will_be_called(self, mock_keystone):

        mock_keystone.return_value.get_endpoints.return_value = {
            'adminURL': 'http://api.end.point'
        }

        patch('identity.views.delete_swift_account', Mock()).start()

        _ = self.view(self.request, project_id='12345abcef')

        mock_keystone = self.mock_vault_keystone.return_value
        mock_keystone.vault_delete_project.assert_called_with('12345abcef')
