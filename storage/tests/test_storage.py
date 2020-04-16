# -*- coding: utf-8 -*-

from unittest.mock import patch, Mock
from unittest import TestCase
import requests

from swiftclient import client

from django.urls import reverse
from django.utils.translation import gettext as _
from django.test.utils import override_settings
from django.contrib.auth.models import Group, User

from storage.tests import fakes
from storage import views

from vault.tests.fakes import fake_request
from vault import utils


class BaseTestCase(TestCase):

    def setUp(self):
        self.request = fake_request()
        self.anonymous_request = fake_request(user=False)
        patch('storage.views.main.actionlog',
              Mock(return_value=None)).start()

    def tearDown(self):
        User.objects.all().delete()
        Group.objects.all().delete()

    @classmethod
    def setUpClass(cls):
        patch('identity.keystone.v3').start()

    @classmethod
    def tearDownClass(cls):
        patch.stopall()


class TestStorage(BaseTestCase):

    def test_containerview_needs_authentication(self):
        response = views.containerview(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_create_container_needs_authentication(self):
        response = views.create_container(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_objectview_needs_authentication(self):
        response = views.objectview(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_delete_container_view_needs_authentication(self):
        response = views.delete_container_view(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_create_object_needs_authentication(self):
        response = views.create_object(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_upload_needs_authentication(self):
        response = views.upload(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_delete_object_view_needs_authentication(self):
        response = views.delete_object_view(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_delete_pseudofolder_needs_authentication(self):
        response = views.delete_pseudofolder(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_create_pseudofolder_needs_authentication(self):
        response = views.create_pseudofolder(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_object_versioning_needs_authentication(self):
        response = views.object_versioning(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    def test_remove_from_cache_needs_authentication(self):
        response = views.remove_from_cache(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    @patch('storage.views.main.client.get_account')
    def test_containerview_redirect_to_dashboard_without_project_in_session(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()
        self.request.session['project_id'] = None

        response = views.containerview(self.request, None)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('change_project'))

    @patch('requests.get')
    @patch('storage.views.main.client.get_account')
    def test_containerview_list_containters(self, mock_get_account, mock_get):
        mock_get_account.return_value = fakes.get_account()
        mock_get.return_value = fakes.FakeRequestResponse(200, headers={"get": {"X-Bla": "Bla", "X-Ble": "Ble"}})
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        project_name = self.request.session.get('project_name')
        response = views.containerview(self.request, project_name)

        self.assertEqual(response.status_code, 200)

        expected = '/p/{}/storage/objects/container1/'.format(project_name)
        self.assertIn(expected, response.content.decode('UTF-8'))

        expected = '/p/{}/storage/objects/container2/'.format(project_name)
        self.assertIn(expected, response.content.decode('UTF-8'))

        expected = '/p/{}/storage/objects/container3/'.format(project_name)
        self.assertIn(expected, response.content.decode('UTF-8'))

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.get_account')
    def test_containerview_clientexception(self, mock_get_account, mock_logging):
        mock_get_account.side_effect = client.ClientException('')
        project_name = self.request.session.get('project_name')
        self.request.META.update({'HTTP_HOST': 'localhost'})

        views.containerview(self.request, project_name)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_get_account.called)
        self.assertTrue(mock_logging.called)

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Unable to list containers'))

    @patch('storage.views.main.client.get_container')
    def test_objectview_list_objects(self, mock_get_container):
        mock_get_container.return_value = fakes.get_container()
        project_name = self.request.session.get('project_name')

        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })

        response = views.objectview(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)

        expected = '/AUTH_1/fakecontainer/obj_pelo_vip.html'
        self.assertIn(expected, response.content.decode('UTF-8'))

        # Botao de views.upload File
        self.assertIn('/p/{}/storage/upload/fakecontainer/'.format(project_name), response.content.decode('UTF-8'))

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.get_container')
    def test_objectview_clientexception(self, mock_get_container, mock_logging):
        mock_get_container.side_effect = client.ClientException('')
        project_name = self.request.session.get('project_name')
        views.objectview(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_get_container.called)
        self.assertTrue(mock_logging.called)

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Access denied'))

    @patch("storage.views.main.actionlog.log")
    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.put_container')
    def test_create_container_valid_form(self, mock_put_container, mock_logging, mock_log):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': 'fakecontainer'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        views.create_container(self.request, project_name)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Container created'))
        self.assertTrue(mock_put_container.called)
        self.assertFalse(mock_logging.called)

        user = self.request.user.username
        mock_log.assert_called_with(user, "create", "fakecontainer")

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.put_container')
    def test_create_container_invalid_form(self, mock_put_container, mock_logging):

        mock_put_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        post = self.request.POST.copy()

        post.update({'containername': ''})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.create_container(self.request, project_name)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 0)
        self.assertFalse(mock_put_container.called)
        self.assertFalse(mock_logging.called)

        self.assertEqual(response.status_code, 200)
        self.assertIn(_('This field is required.'), response.content.decode('UTF-8'))

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.put_container')
    def test_create_container_invalid_container_names(self, mock_put_container, mock_logging):

        mock_put_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        post = self.request.POST.copy()

        post.update({'containername': '.'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.create_container(self.request, project_name)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 0)
        self.assertFalse(mock_put_container.called)
        self.assertFalse(mock_logging.called)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter a valid name consisting of letters, numbers, underscores or hyphens.', response.content.decode('UTF-8'))

        post.update({'containername': '..'})
        self.request.POST = post
        response = views.create_container(self.request, project_name)
        self.assertIn('Enter a valid name consisting of letters, numbers, underscores or hyphens.', response.content.decode('UTF-8'))

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.put_container')
    def test_create_container_fail_to_create(self, mock_put_container, mock_logging):

        mock_put_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': 'fakecontainer'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        views.create_container(self.request, project_name)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Access denied'))
        self.assertTrue(mock_put_container.called)
        self.assertTrue(mock_logging.called)

    @patch('storage.views.main.requests.put')
    def test_create_object_status_201(self, mock_requests_put):
        mock_requests_put.return_value = fakes.FakeRequestResponse(201)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        prefix = ''
        fakecontainer = 'fakecontainer'
        project_name = self.request.session.get('project_name')

        response = views.create_object(self.request, project_name, fakecontainer)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Object created'))
        self.assertTrue(mock_requests_put.called)

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.requests.put')
    def test_create_object_status_201_with_prefix(self, mock_requests_put):
        mock_requests_put.return_value = fakes.FakeRequestResponse(201)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        prefix = 'prefix/'
        fakecontainer = 'fakecontainer'
        project_name = self.request.session.get('project_name')

        response = views.create_object(self.request, project_name, fakecontainer, prefix)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Object created'))
        self.assertTrue(mock_requests_put.called)

        # Transforma em string toda a chamada do Mock, pois nao foi possivel
        #  pegar os argumentos posicionais para validar
        str_call = str(mock_requests_put.call_args)
        self.assertIn('/fakecontainer/prefix/foo.txt', str_call)

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.requests.put')
    def test_create_object_status_401(self, mock_requests_put, mock_logging):
        mock_requests_put.return_value = fakes.FakeRequestResponse(401)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()
        project_name = self.request.session.get('project_name')

        views.create_object(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Access denied'))
        self.assertTrue(mock_requests_put.called)
        self.assertFalse(mock_logging.called)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.requests.put')
    def test_create_object_status_403(self, mock_requests_put, mock_logging):
        mock_requests_put.return_value = fakes.FakeRequestResponse(403)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()
        project_name = self.request.session.get('project_name')

        views.create_object(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Access denied'))
        self.assertTrue(mock_requests_put.called)
        self.assertFalse(mock_logging.called)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.requests.put')
    def test_create_object_status_other_than_above(self, mock_requests_put, mock_logging):
        mock_requests_put.return_value = fakes.FakeRequestResponse(404)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()
        project_name = self.request.session.get('project_name')

        views.create_object(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)

        expected = msg = 'Fail to create object ({0}).'.format(404)
        self.assertEqual(msgs[0].message, expected)
        self.assertTrue(mock_requests_put.called)
        self.assertFalse(mock_logging.called)

    @patch('storage.views.main.delete_container')
    def test_delete_container_view_deletes_with_success(self, mock_delete_container):
        mock_delete_container.return_value = True
        self.request.method = 'DELETE'
        project_name = self.request.session.get('project_name')
        response = views.delete_container_view(self.request, project_name, 'container')

        self.assertTrue(mock_delete_container.called)
        self.assertEqual(response.status_code, 200)
        self.assertIn(_('Container deleted'), response.content.decode('unicode-escape'))

    @patch('storage.views.main.delete_container')
    def test_delete_container_view_deletes_with_failure(self, mock_delete_container):
        mock_delete_container.return_value = False
        self.request.method = 'DELETE'
        project_name = self.request.session.get('project_name')
        response = views.delete_container_view(self.request, project_name, 'container')

        self.assertTrue(mock_delete_container.called)
        self.assertEqual(response.status_code, 500)
        self.assertIn(_('Container delete error'), response.content.decode('UTF-8'))

    @patch('storage.views.main.client.get_object')
    @patch('storage.views.main.client.delete_object')
    @patch("storage.views.main.actionlog.log")
    @patch('storage.views.main.client.delete_container')
    def test_delete_container_without_deleting_objects(self,
                                                       mock_delete_container,
                                                       mock_action_log,
                                                       mock_delete_object,
                                                       mock_get_object):
        fakecontainer = 'fakecontainer'
        resp = views.delete_container(self.request, fakecontainer, force=False)
        self.assertTrue(resp)

        self.assertFalse(mock_get_object.called)
        self.assertFalse(mock_delete_object.called)

        self.assertTrue(mock_delete_container.called)
        self.assertTrue(mock_action_log.called)

    @patch('storage.views.main.client.get_container')
    @patch('storage.views.main.client.delete_object')
    @patch("storage.views.main.actionlog.log")
    @patch('storage.views.main.client.delete_container')
    def test_delete_container_deleting_objects(self, mock_delete_container,
                                               mock_action_log,
                                               mock_delete_object,
                                               mock_get_container):
        fakecontainer = 'fakecontainer'
        mock_get_container.return_value = (None, [{'name': 'object1'}])

        resp = views.delete_container(self.request, fakecontainer, force=True)
        self.assertTrue(resp)

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual('fakecontainer', kargs['container'])
        self.assertEqual('object1', kargs['name'])

        self.assertTrue(mock_delete_container.called)
        self.assertTrue(mock_action_log.called)

    @patch('storage.views.main.client.get_container')
    @patch('storage.views.main.client.delete_object')
    @patch("storage.views.main.actionlog.log")
    @patch('storage.views.main.client.delete_container')
    def test_delete_container_fail_to_get_objects(self, mock_delete_container,
                                                  mock_action_log,
                                                  mock_delete_object,
                                                  mock_get_container):
        fakecontainer = 'fakecontainer'
        mock_get_container.side_effect = client.ClientException('')

        expected = False
        computed = views.delete_container(self.request, fakecontainer, True)
        self.assertEqual(computed, expected)

        self.assertFalse(mock_delete_object.called)
        self.assertFalse(mock_delete_container.called)
        self.assertFalse(mock_action_log.called)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.get_container')
    @patch('storage.views.main.client.delete_object')
    @patch("storage.views.main.actionlog.log")
    @patch('storage.views.main.client.delete_container')
    def test_delete_container_fail_to_delete_container(self,
                                                       mock_delete_container,
                                                       mock_action_log,
                                                       mock_delete_object,
                                                       mock_get_container,
                                                       mock_log_exception):
        fakecontainer = 'fakecontainer'
        mock_delete_container.side_effect = client.ClientException('')
        mock_get_container.return_value = (None, [{'name': 'object1'}])

        expected = False
        computed = views.delete_container(self.request, fakecontainer, True)
        self.assertEqual(computed, expected)

        self.assertTrue(mock_log_exception.called)

        self.assertTrue(mock_delete_object.called)
        self.assertTrue(mock_delete_container.called)

    @patch('storage.views.main.client.put_object')
    def test_create_pseudofolder_with_no_prefix(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': 'fakepseudofolder'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.create_pseudofolder(self.request, project_name, 'fakecontainer')
        expected_redirect_arg = ('Location', '/p/{}/storage/objects/fakecontainer/'.format(project_name))

        self.assertIn(expected_redirect_arg, response.items())

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Pseudofolder created'))
        self.assertTrue(mock_put_object.called)

        name, args, kargs = mock_put_object.mock_calls[0]
        expected_arg = 'application/directory'

        self.assertEqual(expected_arg, kargs['content_type'])

        # Transforma em string toda a chamada do Mock, pois nao foi possivel
        #  pegar os argumentos posicionais para validar
        str_call = str(mock_put_object.call_args)

        self.assertIn(", 'fakepseudofolder/',", str_call)

    @patch('storage.views.main.client.put_object')
    def test_create_pseudofolder_with_prefix(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        prefix = 'prefix/'
        pseudofolder = 'fakepseudofolder'
        project_name = self.request.session.get('project_name')

        post.update({'foldername': pseudofolder})
        self.request.POST = post

        response = views.create_pseudofolder(self.request,
                                            project_name,
                                            'fakecontainer',
                                            prefix)

        expected_redirect_arg = (
                'Location',
                '/p/{}/storage/objects/fakecontainer/{}'.format(project_name, prefix))
        self.assertIn(expected_redirect_arg, response.items())

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Pseudofolder created'))
        self.assertTrue(mock_put_object.called)

        name, args, kargs = mock_put_object.mock_calls[0]
        expected_arg = 'application/directory'

        self.assertEqual(expected_arg, kargs['content_type'])

        # Transforma em string toda a chamada do Mock, pois nao foi possivel pegar
        # os argumentos posicionais para validar
        str_call = str(mock_put_object.call_args)

        expected_foldername = '{0}{1}/'.format(prefix, pseudofolder)
        self.assertIn(expected_foldername, str_call)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.put_object')
    def test_create_pseudofolder_exception(self, mock_put_object, mock_logging):

        mock_put_object.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': 'fakepseudofolder'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        views.create_pseudofolder(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('Access denied'))
        self.assertTrue(mock_put_object.called)
        self.assertTrue(mock_logging.called)

    @patch('storage.views.main.client.put_object')
    def test_create_pseudofolder_invalid_form(self, mock_put_object):
        self.request.method = 'POST'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        post = self.request.POST.copy()

        post.update({'foldername': ''})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.create_pseudofolder(self.request, project_name, 'fakecontainer')

        self.assertFalse(mock_put_object.called)
        self.assertIn(_('This field is required.'), response.content.decode('UTF-8'))

    @patch('storage.views.main.delete_object')
    def test_view_delete_object_inside_a_container(self, mock_delete_object):

        mock_delete_object.return_value = True

        fakecontainer = 'fakecontainer'
        fakeobject_name = 'fakeobject'
        project_name = self.request.session.get('project_name')

        response = views.delete_object_view(self.request,
                                            project_name,
                                            fakecontainer,
                                            fakeobject_name)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, _('Object deleted'))

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.delete_object')
    def test_view_delete_object_inside_a_pseudofolder(self, mock_delete_object):

        mock_delete_object.return_value = True

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'
        fakeobject_name = fakepseudofolder + 'fakeobject'
        project_name = self.request.session.get('project_name')

        response = views.delete_object_view(self.request,
                                            project_name,
                                            fakecontainer,
                                            fakeobject_name)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, _('Object deleted'))

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': fakepseudofolder,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.delete_object')
    def test_view_delete_object_fail_to_delete(self, mock_delete_object):

        mock_delete_object.return_value = False

        fakecontainer = 'fakecontainer'
        fakeobject_name = 'fakeobject'
        project_name = self.request.session.get('project_name')

        response = views.delete_object_view(self.request,
                                            project_name,
                                            fakecontainer,
                                            fakeobject_name)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, _('Access denied'))

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.actionlog.log')
    @patch('storage.views.main.client.delete_object')
    def test_delete_object(self, mock_delete_object, mock_actionlog):

        fakecontainer = 'fakecontainer'
        fakeobject = 'fakeobject'

        response = views.delete_object(self.request, fakecontainer, fakeobject)

        self.assertTrue(response)
        self.assertTrue(mock_actionlog.called)

    @patch('storage.views.main.actionlog.log')
    @patch('storage.views.main.client.delete_object')
    def test_delete_object_fail_to_delete(self, mock_delete_object, mock_actionlog):

        mock_delete_object.side_effect = client.ClientException('')

        fakecontainer = 'fakecontainer'
        fakeobject = 'fakeobject'

        response = views.delete_object(self.request, fakecontainer, fakeobject)

        self.assertFalse(response)
        self.assertTrue(mock_delete_object.called)

    @patch('storage.views.main.client.delete_object')
    @patch('storage.views.main.client.get_container')
    def test_delete_empty_pseudofolder(self, mock_get_container, mock_delete_object):

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'
        project_name = self.request.session.get('project_name')

        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        response = views.delete_pseudofolder(self.request, project_name,
                                             fakecontainer, fakepseudofolder)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_delete_object.called)
        self.assertEqual(msgs[0].message, _('Pseudofolder deleted'))

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual(kargs['name'], fakepseudofolder)
        self.assertEqual(kargs['container'], fakecontainer)

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.client.delete_object')
    @patch('storage.views.main.client.get_container')
    def test_delete_non_empty_pseudofolder(self, mock_get_container, mock_delete_object):

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'
        project_name = self.request.session.get('project_name')

        fakepseudofolder_content = [
            {'name': fakepseudofolder},
            {'name': fakepseudofolder + 'fakeobjeto1'},
            {'name': fakepseudofolder + 'fakeobjeto2'}
        ]

        mock_get_container.return_value = ['stats', fakepseudofolder_content]

        views.delete_pseudofolder(self.request, project_name, fakecontainer, fakepseudofolder)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, 'Pseudofolder and 2 objects deleted.')

        self.assertTrue(mock_delete_object.called)

        kargs = mock_delete_object.mock_calls[0][2]
        self.assertEqual(kargs['name'], fakepseudofolder_content[0]['name'])

        kargs = mock_delete_object.mock_calls[1][2]
        self.assertEqual(kargs['name'], fakepseudofolder_content[1]['name'])

        kargs = mock_delete_object.mock_calls[2][2]
        self.assertEqual(kargs['name'], fakepseudofolder_content[2]['name'])

    @patch('storage.views.main.client.delete_object')
    @patch('storage.views.main.client.get_container')
    def test_delete_non_empty_pseudofolder_with_some_failures(self, mock_get_container, mock_delete_object):
        # TODO: Find a way to simulate one failures among successful deletes
        pass

    @patch('storage.views.main.client.delete_object')
    @patch('storage.views.main.client.get_container')
    def test_delete_empty_pseudofolder_inside_other_pseudofolder(self, mock_get_container, mock_delete_object):

        prefix = 'fakepseudofolder1/'
        fakecontainer = 'fakecontainer'
        fakepseudofolder = prefix + 'fakepseudofolder2/'
        project_name = self.request.session.get('project_name')

        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        response = views.delete_pseudofolder(self.request, project_name,
                                             fakecontainer, fakepseudofolder)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_delete_object.called)
        self.assertEqual(msgs[0].message, _('Pseudofolder deleted'))

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual(kargs['name'], fakepseudofolder)
        self.assertEqual(kargs['container'], fakecontainer)

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.client.delete_object')
    @patch('storage.views.main.client.get_container')
    def test_delete_pseudofolder_fail(self, mock_get_container, mock_delete_object):
        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'
        project_name = self.request.session.get('project_name')

        mock_delete_object.side_effect = client.ClientException('')
        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        views.delete_pseudofolder(self.request, project_name, fakecontainer, fakepseudofolder)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_delete_object.called)
        self.assertEqual(msgs[0].message, _('Fail to delete pseudofolder'))

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual(kargs['name'], fakepseudofolder)
        self.assertEqual(kargs['container'], fakecontainer)

    @patch('storage.views.main.client.get_account')
    def test_render_upload_view(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()
        project_name = self.request.session.get('project_name')

        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })

        response = views.upload(self.request, project_name, 'fakecontainer')

        self.assertIn('enctype="multipart/form-data"', response.content.decode('UTF-8'))

    @patch('storage.views.main.client.get_account')
    def test_render_upload_view_with_prefix(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })

        response = views.upload(self.request, 'fakecontainer', 'prefixTest')

        self.assertIn('prefixTest', response.content.decode('UTF-8'))

    @patch('storage.views.main.client.get_account')
    def test_upload_view_without_temp_key_without_prefix(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        patch('storage.views.main.get_temp_key',
              Mock(return_value=None)).start()

        prefix = ''
        fakecontainer = 'fakecontainer'
        project_name = self.request.session.get('project_name')

        response = views.upload(self.request, project_name, fakecontainer, prefix)

        self.assertEqual(response.status_code, 302)

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.client.get_account')
    def test_upload_view_without_temp_key_with_prefix(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        patch('storage.views.main.get_temp_key',
              Mock(return_value=None)).start()

        prefix = 'prefix/'
        fakecontainer = 'fakecontainer'
        project_name = self.request.session.get('project_name')

        response = views.upload(self.request, project_name, fakecontainer, prefix)

        self.assertEqual(response.status_code, 302)

        headers = dict([i for i in response.items()])
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix,
                                                 'project': project_name})
        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.requests.get')
    def test_download(self, mock_get):
        content = b'ola'
        headers = {'Content-Type': 'fake/object'}
        project_name = self.request.session.get('project_name')
        mock_get.return_value = fakes.FakeRequestResponse(content=content,
                                                          headers=headers)
        response = views.download(self.request, project_name, 'fakecontainer', 'fakeobject')

        computed_headers = dict([i for i in response.items()])

        self.assertEqual(response.content, content)
        self.assertEqual(headers, computed_headers)

    @patch('storage.views.main.requests.head')
    def test_metadataview_return_headers_from_container(self, mock_head):
        headers = {'content-type': 'fake/container'}
        project_name = self.request.session.get('project_name')
        mock_head.return_value = fakes.FakeRequestResponse(content='',
                                                          headers=headers)
        response = views.metadataview(self.request, project_name, 'fakecontainer')

        self.assertIn('fake/container', response.content.decode('UTF-8'))

    @patch('storage.views.main.requests.head')
    def test_metadataview_return_headers_from_object(self, mock_head):
        headers = {'content-type': 'fake/object'}
        mock_head.return_value = fakes.FakeRequestResponse(content='',
                                                          headers=headers)
        response = views.metadataview(self.request,
                                      'fakecontainer',
                                      'fakeobject')

        self.assertIn('fake/object', response.content.decode('UTF-8'))

    @patch('storage.views.main.actionlog.log')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.put_container')
    def test_enable_versioning(self,
                               mock_put_container,
                               mock_post_container,
                               mock_actionlog):

        container = 'fakecontainer'
        computed = views.enable_versioning(self.request, container)

        self.assertEqual(computed, True)
        self.assertTrue(mock_put_container.called)

        kargs = mock_post_container.mock_calls[0][2]

        headers = kargs['headers']
        version_location = '_version_{}'.format(container)
        self.assertEqual(version_location, headers['x-versions-location'])

        # Create container/update container
        self.assertEqual(mock_actionlog.call_count, 2)

    @patch('storage.views.main.actionlog.log')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.put_container')
    def test_enable_versioning_fail_to_create_container(self,
                                                        mock_put_container,
                                                        mock_post_container,
                                                        mock_actionlog):

        mock_put_container.side_effect = client.ClientException('')

        container = 'fakecontainer'
        computed = views.enable_versioning(self.request, container)

        self.assertEqual(computed, False)

        self.assertFalse(mock_post_container.called)

        self.assertEqual(mock_actionlog.call_count, 0)

    @patch('storage.views.main.actionlog.log')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.put_container')
    def test_enable_versioning_fail_to_update_container(self,
                                                        mock_put_container,
                                                        mock_post_container,
                                                        mock_actionlog):

        mock_post_container.side_effect = client.ClientException('')

        container = 'fakecontainer'
        computed = views.enable_versioning(self.request, container)

        self.assertEqual(computed, False)

        self.assertTrue(mock_post_container.called)

        self.assertEqual(mock_actionlog.call_count, 1)

    @patch('storage.views.main.actionlog.log')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.delete_container')
    @patch('storage.views.main.client.head_container')
    def test_disable_versioning(self,
                                mock_head_container,
                                mock_delete_container,
                                mock_post_container,
                                mock_actionlog):

        version_location = '_version_fakecontainer'
        mock_head_container.return_value = {'x-versions-location': version_location}

        container = 'fakecontainer'
        computed = views.disable_versioning(self.request, container)

        self.assertEqual(computed, True)

        kargs = mock_delete_container.mock_calls[0][2]

        self.assertEqual(version_location, kargs['container'])

        self.assertEqual(mock_actionlog.call_count, 1)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.delete_container')
    @patch('storage.views.main.client.head_container')
    def test_disable_versioning_fail_to_get_container_headers(self,
                                                       mock_head_container,
                                                       mock_delete_container,
                                                       mock_post_container,
                                                       mock_logging):

        mock_head_container.side_effect = client.ClientException('')

        container = 'fakecontainer'
        computed = views.disable_versioning(self.request, container)

        self.assertEqual(computed, False)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, _('Access denied'))

        self.assertEqual(mock_logging.call_count, 1)

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.delete_container')
    @patch('storage.views.main.client.head_container')
    def test_disable_versioning_fail_to_update_container_header(self,
                                                       mock_head_container,
                                                       mock_delete_container,
                                                       mock_post_container,
                                                       mock_logging):

        mock_post_container.side_effect = client.ClientException('')

        version_location = '_version_fakecontainer'
        mock_head_container.return_value = {'x-versions-location': version_location}

        container = 'fakecontainer'
        computed = views.disable_versioning(self.request, container)

        self.assertEqual(computed, False)

        self.assertFalse(mock_delete_container.called)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, _('Access denied'))

        self.assertEqual(mock_logging.call_count, 1)

    @patch('storage.views.main.render')
    @patch('storage.views.main.client.head_container')
    def test_object_versioning_view_versioning_disabled(self,
                                                        mock_head_container,
                                                        mock_render):
        mock_head_container.return_value = {}
        project_name = self.request.session.get('project_name')

        views.object_versioning(self.request, project_name, 'fakecontainer')

        kargs = mock_render.mock_calls[0][1]
        computed = kargs[2]

        expected = {'objects': utils.generic_pagination([], 1),
                    'container': 'fakecontainer',
                    'version_location': None}

        self.assertEqual(str(computed['objects']), str(expected['objects']))
        self.assertEqual(computed['container'], expected['container'])
        self.assertEqual(computed['version_location'], expected['version_location'])

    @patch('storage.views.main.render')
    @patch('storage.views.main.client.get_container')
    @patch('storage.views.main.client.head_container')
    def test_object_versioning_view_versioning_enabled(self,
                                                       mock_head_container,
                                                       mock_get_container,
                                                       mock_render):
        mock_head_container.return_value = {'x-versions-location': 'abc'}
        mock_get_container.return_value = (None, [])
        project_name = self.request.session.get('project_name')

        views.object_versioning(self.request, project_name, 'fakecontainer')

        kargs = mock_render.mock_calls[0][1]
        computed = kargs[2]

        expected = {'objects': utils.generic_pagination([], 1),
                    'container': 'fakecontainer',
                    'version_location': 'abc'}

        self.assertEqual(str(computed['objects']), str(expected['objects']))
        self.assertEqual(computed['container'], expected['container'])
        self.assertEqual(computed['version_location'], expected['version_location'])

    @patch('storage.views.main.enable_versioning')
    def test_object_versioning_view_enabling_versioning(self, mock_enable):

        post = self.request.method = 'POST'
        post = self.request.POST.copy()
        project_name = self.request.session.get('project_name')

        post.update({'action': 'enable'})
        self.request.POST = post

        response = views.object_versioning(self.request, project_name, 'fakecontainer')

        self.assertEqual(mock_enable.call_count, 1)

        headers = dict([i for i in response.items()])
        expected = reverse('object_versioning',
                           kwargs={'project': project_name, 'container': 'fakecontainer'})

        self.assertEqual(headers['Location'], expected)

    @patch('storage.views.main.disable_versioning')
    def test_object_versioning_view_disabling_versioning(self, mock_disable):

        post = self.request.method = 'POST'
        post = self.request.POST.copy()
        project_name = self.request.session.get('project_name')

        post.update({'action': 'disable'})
        self.request.POST = post

        response = views.object_versioning(self.request, project_name, 'fakecontainer')

        self.assertEqual(mock_disable.call_count, 1)

        headers = dict([i for i in response.items()])
        expected = reverse('object_versioning',
                           kwargs={'project': project_name, 'container': 'fakecontainer'})

        self.assertEqual(headers['Location'], expected)

    @override_settings(SWIFT_HIDE_PREFIXES=['.'])
    @patch('storage.views.main.client.get_account')
    def test_filter_containers_with_prefix_listed_in_SWIFT_HIDE_PREFIXES(self, mock_get_account):
        fake_get_acc = fakes.get_account()
        containers = [{'count': 4, 'bytes': 4, 'name': '.container4'}]
        project_name = self.request.session.get('project_name')

        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })

        mock_get_account.return_value = (fake_get_acc[0], containers)
        response = views.containerview(self.request, project_name)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('/storage/objects/.container4/', response.content.decode('UTF-8'))


class TestStorageAcls(BaseTestCase):

    def test_edit_acl_needs_authentication(self):
        response = views.edit_acl(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    @patch('storage.views.main.client.head_container')
    def test_edit_acl_list_acls_container_public(self, mock_get_container):
        """
        Verify the ACL list for a container public and
        if the "Make private" action is available
        """
        mock_get_container.return_value = {
            'x-container-read': '.r:*',
            'x-container-write': '',
        }
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Add ACL to container fakecontainer', response.content.decode('UTF-8'))
        self.assertIn('Make private', response.content.decode('UTF-8'))
        self.assertIn('Add ACL', response.content.decode('UTF-8'))
        self.assertIn('.r:*', response.content.decode('UTF-8'))

    @patch('storage.views.main.client.head_container')
    def test_edit_acl_list_acls_container_private(self, mock_get_container):
        """
        Verify the ACL list for a private container with no ACLS and
        if the "Make Public" action is available
        """
        mock_get_container.return_value = {
            'x-container-read': '',
            'x-container-write': '',
        }
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Make public', response.content.decode('UTF-8'))
        self.assertIn('Add ACL', response.content.decode('UTF-8'))

        expected = 'There are no ACLs for this container yet. Add a new ACL by clicking the red button.'
        self.assertIn(expected, response.content.decode('UTF-8'))

    @patch('storage.views.main.client.head_container')
    def test_edit_acl_private_container_but_public_for_read_and_write_for_an_user_and_project(self, mock_head_container):
        """
        Verify if it's properly listing container's acl and
        if the "Make Public" action is available
        """
        mock_head_container.return_value = {
            'x-container-read': 'projectfake:userfake',
            'x-container-write': 'projectfake:userfake',
        }
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Make public', response.content.decode('UTF-8'))
        self.assertIn('Add ACL', response.content.decode('UTF-8'))
        self.assertIn('projectfake:userfake', response.content.decode('UTF-8'))

    @patch('storage.views.main.client.head_container')
    def test_edit_acl_public_container_and_public_for_read_for_more_than_one_user_and_project(self, mock_head_container):
        """
        Verify if it's properly listing container's acl for a public container
        and if Make Private is available
        """
        mock_head_container.return_value = {
            'x-container-read': '.r:*,projectfake:userfake',
            'x-container-write': 'projectfake2:userfake2',
        }
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Make private', response.content.decode('UTF-8'))
        self.assertIn('Add ACL', response.content.decode('UTF-8'))
        self.assertIn('projectfake:userfake', response.content.decode('UTF-8'))
        self.assertIn('projectfake2:userfake2', response.content.decode('UTF-8'))

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_grant_read_and_write_permission_for_a_project_and_user(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-read': '',
            'x-container-write': '',
        }

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({
                'username': 'projectfake:userfake',
                'read': 'On',
                'write': 'On'
        })

        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': ',projectfake:userfake',
            'X-Container-Read': ',projectfake:userfake'
        }
        self.assertEqual(expected_arg, kargs['headers'])

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, _('ACLs updated'))

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_expcetion_on_grant_read_and_write_permission_for_a_project_and_user(self, mock_head_container, mock_post_container, mock_logging):
        mock_head_container.return_value = {
            'x-container-read': '',
            'x-container-write': '',
        }

        mock_post_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({
                'username': 'projectfake:userfake',
                'read': 'On',
                'write': 'On'
        })

        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(msgs), 1)
        self.assertTrue(mock_logging.called)
        self.assertEqual(msgs[0].message, _('ACL update failed'))

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_make_private(self, mock_head_container, mock_post_container):
        """
            Verify if the action "Making Private" is
            removing ".r:*" from x-container-read header
        """
        mock_head_container.return_value = {
            'x-container-read': '.r:*,projectfake:userfake',
            'x-container-write': 'projectfake2:userfake2',
        }

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': '.r:*,.rlistings'})
        self.request.GET = get
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_post_container.called)

        name, args, kargs = mock_post_container.mock_calls[0]
        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2,',
            'X-Container-Read': 'projectfake:userfake,'
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_make_public(self, mock_head_container, mock_post_container):
        """
            Verify if the action "Making Public" is
            including ".r:*" in x-container-read header
        """
        mock_head_container.return_value = {
            'x-container-read': 'projectfake:userfake',
            'x-container-write': 'projectfake2:userfake2',
        }

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'username': '.r:*', 'read': 'On'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_post_container.called)

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2',
            'X-Container-Read': 'projectfake:userfake,.r:*'
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_delete_acl_for_user_in_a_public_container(self, mock_head_container, mock_post_container):
        """ Verify if is deleting the correct ACL """
        mock_head_container.return_value = {
            'x-container-read': '.r:*,projectfake:userfake',
            'x-container-write': 'projectfake:userfake,projectfake2:userfake2',
        }

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': 'projectfake:userfake'})
        self.request.GET = get
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2,',
            'X-Container-Read': '.r:*,'
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_delete_acl_for_user_in_a_private_container(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-read': 'projectfake:userfake',
            'x-container-write': 'projectfake:userfake,projectfake2:userfake2',
        }

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': 'projectfake:userfake'})
        self.request.GET = get
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        self.assertEqual(response.status_code, 200)

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2,',
            'X-Container-Read': ''
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('storage.views.main.log.exception')
    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_edit_acl_delete_acl_exception(self, mock_head_container, mock_post_container, mock_logging):
        mock_head_container.return_value = {
            'x-container-read': 'projectfake:userfake',
            'x-container-write': 'projectfake:userfake',
        }

        mock_post_container.side_effect = client.ClientException('')

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': 'projectfake:userfake'})
        self.request.GET = get
        project_name = self.request.session.get('project_name')

        response = views.edit_acl(self.request, project_name, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertTrue(mock_logging.called)
        self.assertEqual(msgs[0].message, _('ACL update failed'))
        self.assertIn('projectfake:userfake', response.content.decode('UTF-8'))


class TestStorageCORS(BaseTestCase):

    def test_edit_cors_needs_authentication(self):
        response = views.edit_cors(self.anonymous_request)

        self.assertEqual(response.status_code, 302)

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_define_novo_host_para_regra_de_cors_no_container(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-meta-access-control-allow-origin': '',
        }

        self.request.method = 'POST'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        post = self.request.POST.copy()
        project_name = self.request.session.get('project_name')

        post.update({'host': 'globo.com'})
        self.request.POST = post

        views.edit_cors(self.request, project_name, 'fakecontainer')

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {'x-container-meta-access-control-allow-origin': 'globo.com'}

        self.assertEqual(expected_arg, kargs['headers'])

    @patch('storage.views.main.client.post_container')
    @patch('storage.views.main.client.head_container')
    def test_remove_host_da_regra_de_cors_do_container(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-meta-access-control-allow-origin': 'globo.com globoi.com',
        }

        self.request.method = 'GET'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        get = self.request.GET.copy()
        project_name = self.request.session.get('project_name')

        get.update({'delete': 'globo.com'})
        self.request.GET = get

        views.edit_cors(self.request, project_name, 'fakecontainer')

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {'x-container-meta-access-control-allow-origin': 'globoi.com'}

        self.assertEqual(expected_arg, kargs['headers'])

    @patch('storage.views.main.requests.post')
    def test_remove_from_cache_status_201(self, mock_requests_post):
        mock_requests_post.return_value = fakes.FakeRequestResponse(201)

        self.request.method = 'POST'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        post = self.request.POST.copy()

        post.update({'urls': 'http://localhost/1\r\nhttp://localhost/2'})
        self.request.POST = post
        project_name = self.request.session.get('project_name')

        response = views.remove_from_cache(self.request, project_name)

        host, kargs = mock_requests_post.call_args

        expected_json = {
            'json': {
                'url': [u'http://localhost/1', u'http://localhost/2'],
                'user': self.request.user.username
            }
        }

        # Verifica se a chamada para a API estava com os argumentos corretos
        self.assertEqual(expected_json, kargs)
