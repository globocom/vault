# -*- coding:utf-8 -*-

from mock import Mock, patch
from unittest import TestCase

from identity.tests.fakes import FakeResource
from identity.views import ListProjectView, CreateProjectView, UpdateProjectView
from identity.tests.fakes import AreaFactory, AreaProjectsFactory, \
    GroupProjectsFactory
from vault.tests.fakes import fake_request


class ListProjectTest(TestCase):

    def setUp(self):
        self.view = ListProjectView.as_view()
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
        # self.request.user.groups = [GroupFactory(id=1)]

        patch('actionlogger.ActionLogger.log',
              Mock(return_value=None)).start()

        self.mock_keystone_is_allowed = patch('identity.keystone.Keystone._is_allowed_to_connect').start()

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

        self.assertIn('This field is required', response.content)

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

        self.assertIn('This field is required', response.content)

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

        self.assertIn('Project description cannot be empty.', response.content)

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

        self.assertIn('Project Name must be an alphanumeric.', response.content)

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

    def test_create_success_screen(self):

        response = self.view(self.request)


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

        self.mock_keystone_is_allowed = patch('identity.keystone.Keystone._is_allowed_to_connect').start()
        self.mock_area = patch('identity.forms.Area.objects.all').start()
        self.mock_area.return_value = [AreaFactory(id=1)]

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

        self.assertIn('This field is required', response.content)

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
