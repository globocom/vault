# -*- coding:utf-8 -*-

from mock import patch, Mock
from unittest import TestCase

import swiftclient
from swiftclient import client

from django.core.urlresolvers import reverse

from swiftbrowser.tests import fakes
from swiftbrowser import views

from vault.tests.fakes import fake_request
from vault import utils


class TestSwiftbrowser(TestCase):

    def setUp(self):

        self.user = fakes.FakeUser(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated = lambda: True
        self.request = fake_request(user=self.user)

    def tearDown(self):
        patch.stopall()

    def test_containerview_needs_authentication(self):
        """ Verify if views.containerview is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.containerview(self.request)

        self.assertEqual(response.status_code, 302)

    def test_create_container_needs_authentication(self):
        """ Verify if views.create_container is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.objectview(self.request)

        self.assertEqual(response.status_code, 302)

    def test_objectview_needs_authentication(self):
        """ Verify if views.objectview is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.objectview(self.request)

        self.assertEqual(response.status_code, 302)

    def test_delete_container_view_needs_authentication(self):
        """ Verify if views.delete_container is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.delete_container_view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_create_object_needs_authentication(self):
        """ Verify if views.create_object is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.create_object(self.request)

        self.assertEqual(response.status_code, 302)

    def test_upload_needs_authentication(self):
        """ Verify if views.upload is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.upload(self.request)

        self.assertEqual(response.status_code, 302)

    def test_delete_object_view_needs_authentication(self):
        """ Verify if views.delete_object is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.delete_object_view(self.request)

        self.assertEqual(response.status_code, 302)

    def test_delete_pseudofolder_needs_authentication(self):
        """ Verify if views.delete_pseudofolder is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.delete_pseudofolder(self.request)

        self.assertEqual(response.status_code, 302)

    def test_create_pseudofolder_needs_authentication(self):
        """ Verify if views.create_pseudofolder is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.create_pseudofolder(self.request)

        self.assertEqual(response.status_code, 302)

    def test_object_versioning_needs_authentication(self):
        """ Verify if views.object_versioning is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.object_versioning(self.request)

        self.assertEqual(response.status_code, 302)

    @patch('swiftbrowser.views.client.get_account')
    def test_containerview_redirect_to_dashboard_without_project_in_session(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()
        self.request.session['project_id'] = None
        response = views.containerview(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    @patch('swiftbrowser.views.client.get_account')
    def test_containerview_list_containters(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()
        response = views.containerview(self.request)

        self.assertEqual(response.status_code, 200)

        expected = '/storage/objects/container1/'
        self.assertIn(expected, response.content)

        expected = '/storage/objects/container2/'
        self.assertIn(expected, response.content)

        expected = '/storage/objects/container3/'
        self.assertIn(expected, response.content)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.get_account')
    def test_containerview_clientexception(self, mock_get_account, mock_logging):
        mock_get_account.side_effect = client.ClientException('')
        response = views.containerview(self.request)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_get_account.called)
        self.assertTrue(mock_logging.called)

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Unable to list containers')

    @patch('swiftbrowser.views.client.get_container')
    def test_objectview_list_objects(self, mock_get_container):
        mock_get_container.return_value = fakes.get_container()
        response = views.objectview(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)

        expected = 'http://fakepublicurl/fakecontainer/obj_pelo_vip.html'
        self.assertIn(expected, response.content)

        expected = '"/storage/download/fakecontainer/ok'
        self.assertIn(expected, response.content)

        # Botao de views.upload File
        self.assertIn('/storage/upload/fakecontainer/', response.content)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.get_container')
    def test_objectview_clientexception(self, mock_get_container, mock_logging):
        mock_get_container.side_effect = client.ClientException('')
        response = views.objectview(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_get_container.called)
        self.assertTrue(mock_logging.called)

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Access denied.')

    @patch("swiftbrowser.views.actionlog.log")
    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.put_container')
    def test_create_container_valid_form(self, mock_put_container, mock_logging, mock_log):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': 'fakecontainer'})
        self.request.POST = post

        response = views.create_container(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Container created.')
        self.assertTrue(mock_put_container.called)
        self.assertFalse(mock_logging.called)
        mock_log.assert_called_with("user", "create", "fakecontainer")

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.put_container')
    def test_create_container_invalid_form(self, mock_put_container, mock_logging):

        mock_put_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': ''})
        self.request.POST = post

        response = views.create_container(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 0)
        self.assertFalse(mock_put_container.called)
        self.assertFalse(mock_logging.called)

        self.assertEqual(response.status_code, 200)
        self.assertIn('This field is required.', response.content)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.put_container')
    def test_create_container_invalid_container_names(self, mock_put_container, mock_logging):

        mock_put_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': '.'})
        self.request.POST = post

        response = views.create_container(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 0)
        self.assertFalse(mock_put_container.called)
        self.assertFalse(mock_logging.called)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Enter a valid name consisting of letters, numbers, underscores or hyphens.', response.content)

        post.update({'containername': '..'})
        self.request.POST = post
        response = views.create_container(self.request)
        self.assertIn('Enter a valid name consisting of letters, numbers, underscores or hyphens.', response.content)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.put_container')
    def test_create_container_fail_to_create(self, mock_put_container, mock_logging):

        mock_put_container.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'containername': 'fakecontainer'})
        self.request.POST = post

        response = views.create_container(self.request)
        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Access denied.')
        self.assertTrue(mock_put_container.called)
        self.assertTrue(mock_logging.called)

    @patch('swiftbrowser.views.requests.put')
    def test_create_object_status_201(self, mock_requests_put):
        mock_requests_put.return_value = fakes.FakeRequestResponse(201)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        prefix = ''
        fakecontainer = 'fakecontainer'

        response = views.create_object(self.request, fakecontainer)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Object created.')
        self.assertTrue(mock_requests_put.called)

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.requests.put')
    def test_create_object_status_201_with_prefix(self, mock_requests_put):
        mock_requests_put.return_value = fakes.FakeRequestResponse(201)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        prefix = 'prefix/'
        fakecontainer = 'fakecontainer'

        response = views.create_object(self.request, fakecontainer, prefix)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Object created.')
        self.assertTrue(mock_requests_put.called)

        # Transforma em string toda a chamada do Mock, pois nao foi possivel
        #  pegar os argumentos posicionais para validar
        str_call = str(mock_requests_put.call_args)
        self.assertIn('/fakecontainer/prefix/foo.txt', str_call)

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.requests.put')
    def test_create_object_status_401(self, mock_requests_put, mock_logging):
        mock_requests_put.return_value = fakes.FakeRequestResponse(401)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        response = views.create_object(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Access denied.')
        self.assertTrue(mock_requests_put.called)
        self.assertFalse(mock_logging.called)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.requests.put')
    def test_create_object_status_403(self, mock_requests_put, mock_logging):
        mock_requests_put.return_value = fakes.FakeRequestResponse(403)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        response = views.create_object(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Access denied.')
        self.assertTrue(mock_requests_put.called)
        self.assertFalse(mock_logging.called)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.requests.put')
    def test_create_object_status_other_than_above(self, mock_requests_put, mock_logging):
        mock_requests_put.return_value = fakes.FakeRequestResponse(404)
        self.request.FILES['file1'] = fakes.get_temporary_text_file()

        response = views.create_object(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)

        expected = msg = 'Fail to create object ({0}).'.format(404)
        self.assertEqual(msgs[0].message, expected)
        self.assertTrue(mock_requests_put.called)
        self.assertFalse(mock_logging.called)

    @patch('swiftbrowser.views.delete_container')
    def test_delete_container_view_deletes_with_success(self, mock_delete_container):

        mock_delete_container.return_value = True
        views.delete_container_view(self.request, container='container')

        self.assertTrue(mock_delete_container.called)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, 'Container deleted.')

    @patch('swiftbrowser.views.delete_container')
    def test_delete_container_view_deletes_with_failure(self, mock_delete_container):

        mock_delete_container.return_value = False
        views.delete_container_view(self.request, container='container')

        self.assertTrue(mock_delete_container.called)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, 'Access denied.')

    @patch('swiftbrowser.views.client.get_object')
    @patch('swiftbrowser.views.client.delete_object')
    @patch("swiftbrowser.views.actionlog.log")
    @patch('swiftbrowser.views.client.delete_container')
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

    @patch('swiftbrowser.views.client.get_container')
    @patch('swiftbrowser.views.client.delete_object')
    @patch("swiftbrowser.views.actionlog.log")
    @patch('swiftbrowser.views.client.delete_container')
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

    @patch('swiftbrowser.views.client.get_container')
    @patch('swiftbrowser.views.client.delete_object')
    @patch("swiftbrowser.views.actionlog.log")
    @patch('swiftbrowser.views.client.delete_container')
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

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.get_container')
    @patch('swiftbrowser.views.client.delete_object')
    @patch("swiftbrowser.views.actionlog.log")
    @patch('swiftbrowser.views.client.delete_container')
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

    @patch('swiftbrowser.views.client.put_object')
    def test_create_pseudofolder_with_no_prefix(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': 'fakepseudofolder'})
        self.request.POST = post

        response = views.create_pseudofolder(self.request, 'fakecontainer')

        expected_redirect_arg = ('Location', '/storage/objects/fakecontainer/')
        self.assertIn(expected_redirect_arg, response.items())

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Pseudofolder created.')
        self.assertTrue(mock_put_object.called)

        name, args, kargs = mock_put_object.mock_calls[0]
        expected_arg = 'application/directory'

        self.assertEqual(expected_arg, kargs['content_type'])

        # Transforma em string toda a chamada do Mock, pois nao foi possivel
        #  pegar os argumentos posicionais para validar
        str_call = str(mock_put_object.call_args)

        self.assertIn(", 'fakepseudofolder/',", str_call)

    @patch('swiftbrowser.views.client.put_object')
    def test_create_pseudofolder_with_prefix(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        prefix = 'prefix/'
        pseudofolder = 'fakepseudofolder'

        post.update({'foldername': pseudofolder})
        self.request.POST = post

        response = views.create_pseudofolder(self.request,
                                            'fakecontainer',
                                            prefix)

        expected_redirect_arg = (
                'Location',
                '/storage/objects/fakecontainer/{0}'.format(prefix))
        self.assertIn(expected_redirect_arg, response.items())

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Pseudofolder created.')
        self.assertTrue(mock_put_object.called)

        name, args, kargs = mock_put_object.mock_calls[0]
        expected_arg = 'application/directory'

        self.assertEqual(expected_arg, kargs['content_type'])

        # Transforma em string toda a chamada do Mock, pois nao foi possivel pegar
        # os argumentos posicionais para validar
        str_call = str(mock_put_object.call_args)

        expected_foldername = '{0}{1}/'.format(prefix, pseudofolder)
        self.assertIn(expected_foldername, str_call)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.put_object')
    def test_create_pseudofolder_exception(self, mock_put_object, mock_logging):

        mock_put_object.side_effect = client.ClientException('')

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': 'fakepseudofolder'})
        self.request.POST = post

        response = views.create_pseudofolder(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'Access denied.')
        self.assertTrue(mock_put_object.called)
        self.assertTrue(mock_logging.called)

    @patch('swiftbrowser.views.client.put_object')
    def test_create_pseudofolder_invalid_form(self, mock_put_object):
        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'foldername': ''})
        self.request.POST = post

        response = views.create_pseudofolder(self.request, 'fakecontainer')

        self.assertFalse(mock_put_object.called)
        self.assertIn('This field is required.', response.content)

    @patch('swiftbrowser.views.delete_object')
    def test_view_delete_object_inside_a_container(self, mock_delete_object):

        mock_delete_object.return_value = True

        fakecontainer = 'fakecontainer'
        fakeobject_name = 'fakeobject'

        response = views.delete_object_view(self.request,
                                            fakecontainer,
                                            fakeobject_name)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, 'Object deleted.')

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.delete_object')
    def test_view_delete_object_inside_a_pseudofolder(self, mock_delete_object):

        mock_delete_object.return_value = True

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'
        fakeobject_name = fakepseudofolder + 'fakeobject'

        response = views.delete_object_view(self.request,
                                            fakecontainer,
                                            fakeobject_name)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, 'Object deleted.')

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': fakepseudofolder})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.delete_object')
    def test_view_delete_object_fail_to_delete(self, mock_delete_object):

        mock_delete_object.return_value = False

        fakecontainer = 'fakecontainer'
        fakeobject_name = 'fakeobject'

        response = views.delete_object_view(self.request,
                                            fakecontainer,
                                            fakeobject_name)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, 'Access denied.')

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.actionlog.log')
    @patch('swiftbrowser.views.client.delete_object')
    def test_delete_object(self, mock_delete_object, mock_actionlog):

        fakecontainer = 'fakecontainer'
        fakeobject = 'fakeobject'

        response = views.delete_object(self.request, fakecontainer, fakeobject)

        self.assertTrue(response)
        self.assertTrue(mock_actionlog.called)

    @patch('swiftbrowser.views.actionlog.log')
    @patch('swiftbrowser.views.client.delete_object')
    def test_delete_object_fail_to_delete(self, mock_delete_object, mock_actionlog):

        mock_delete_object.side_effect = client.ClientException('')

        fakecontainer = 'fakecontainer'
        fakeobject = 'fakeobject'

        response = views.delete_object(self.request, fakecontainer, fakeobject)

        self.assertFalse(response)
        self.assertTrue(mock_delete_object.called)

    @patch('swiftbrowser.views.client.delete_object')
    @patch('swiftbrowser.views.client.get_container')
    def test_delete_empty_pseudofolder(self, mock_get_container, mock_delete_object):

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'

        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        response = views.delete_pseudofolder(self.request, fakecontainer,
                                             fakepseudofolder)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_delete_object.called)
        self.assertEqual(msgs[0].message, 'Pseudofolder deleted.')

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual(kargs['name'], fakepseudofolder)
        self.assertEqual(kargs['container'], fakecontainer)

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.client.delete_object')
    @patch('swiftbrowser.views.client.get_container')
    def test_delete_non_empty_pseudofolder(self, mock_get_container, mock_delete_object):

        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'

        fakepseudofolder_content = [
            {'name': fakepseudofolder},
            {'name': fakepseudofolder + 'fakeobjeto1'},
            {'name': fakepseudofolder + 'fakeobjeto2'}
        ]

        mock_get_container.return_value = ['stats', fakepseudofolder_content]

        response = views.delete_pseudofolder(self.request, fakecontainer,
                                             fakepseudofolder)

        msgs = [msg for msg in self.request._messages]
        self.assertEqual(msgs[0].message, 'Pseudofolder and 2 objects deleted.')

        self.assertTrue(mock_delete_object.called)

        kargs = mock_delete_object.mock_calls[0][2]
        self.assertEqual(kargs['name'], fakepseudofolder_content[0]['name'])

        kargs = mock_delete_object.mock_calls[1][2]
        self.assertEqual(kargs['name'], fakepseudofolder_content[1]['name'])

        kargs = mock_delete_object.mock_calls[2][2]
        self.assertEqual(kargs['name'], fakepseudofolder_content[2]['name'])

    @patch('swiftbrowser.views.client.delete_object')
    @patch('swiftbrowser.views.client.get_container')
    def test_delete_non_empty_pseudofolder_with_some_failures(self, mock_get_container, mock_delete_object):
        # TODO: Find a way to simulate one failures among successful deletes
        pass

    @patch('swiftbrowser.views.client.delete_object')
    @patch('swiftbrowser.views.client.get_container')
    def test_delete_empty_pseudofolder_inside_other_pseudofolder(self, mock_get_container, mock_delete_object):

        prefix = 'fakepseudofolder1/'
        fakecontainer = 'fakecontainer'
        fakepseudofolder = prefix + 'fakepseudofolder2/'

        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        response = views.delete_pseudofolder(self.request, fakecontainer,
                                             fakepseudofolder)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_delete_object.called)
        self.assertEqual(msgs[0].message, 'Pseudofolder deleted.')

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual(kargs['name'], fakepseudofolder)
        self.assertEqual(kargs['container'], fakecontainer)

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.client.delete_object')
    @patch('swiftbrowser.views.client.get_container')
    def test_delete_pseudofolder_fail(self, mock_get_container, mock_delete_object):
        fakecontainer = 'fakecontainer'
        fakepseudofolder = 'fakepseudofolder/'

        mock_delete_object.side_effect = client.ClientException('')
        mock_get_container.return_value = ['stats', [{'name': fakepseudofolder}]]

        response = views.delete_pseudofolder(self.request, fakecontainer,
                                             fakepseudofolder)

        msgs = [msg for msg in self.request._messages]

        self.assertTrue(mock_delete_object.called)
        self.assertEqual(msgs[0].message, 'Fail to delete pseudofolder.')

        kargs = mock_delete_object.mock_calls[0][2]

        self.assertEqual(kargs['name'], fakepseudofolder)
        self.assertEqual(kargs['container'], fakecontainer)

    @patch('swiftbrowser.views.client.get_account')
    def test_render_upload_view(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        response = views.upload(self.request, 'fakecontainer')

        self.assertIn('enctype="multipart/form-data"', response.content)

    @patch('swiftbrowser.views.client.get_account')
    def test_render_upload_view_with_prefix(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        response = views.upload(self.request, 'fakecontainer', 'prefixTest')

        self.assertIn('prefixTest', response.content)

    @patch('swiftbrowser.views.client.get_account')
    def test_upload_view_without_temp_key_without_prefix(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        patch('swiftbrowser.views.get_temp_key',
              Mock(return_value=None)).start()

        prefix = ''
        fakecontainer = 'fakecontainer'

        response = views.upload(self.request, fakecontainer, prefix)

        self.assertEqual(response.status_code, 302)

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.client.get_account')
    def test_upload_view_without_temp_key_with_prefix(self, mock_get_account):
        mock_get_account.return_value = fakes.get_account()

        patch('swiftbrowser.views.get_temp_key',
              Mock(return_value=None)).start()

        prefix = 'prefix/'
        fakecontainer = 'fakecontainer'

        response = views.upload(self.request, fakecontainer, prefix)

        self.assertEqual(response.status_code, 302)

        location = response.items()[1][1]
        expected = reverse('objectview', kwargs={'container': fakecontainer,
                                                 'prefix': prefix})
        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.requests.get')
    def test_download(self, mock_get):
        content = 'ola'
        headers = {'content-type': 'fake/object'}
        mock_get.return_value = fakes.FakeRequestResponse(content=content,
                                                          headers=headers)
        response = views.download(self.request, 'fakecontainer', 'fakeobject')

        computed_headers = response.serialize_headers()

        self.assertEqual(response.content, content)
        self.assertIn(headers['content-type'], computed_headers)

    @patch('swiftbrowser.views.requests.get')
    def test_metadataview_return_headers_from_container(self, mock_get):
        headers = {'content-type': 'fake/container'}
        mock_get.return_value = fakes.FakeRequestResponse(content='',
                                                          headers=headers)
        response = views.metadataview(self.request, 'fakecontainer')

        self.assertIn('fake/container', response.content)

    @patch('swiftbrowser.views.requests.get')
    def test_metadataview_return_headers_from_object(self, mock_get):
        headers = {'content-type': 'fake/object'}
        mock_get.return_value = fakes.FakeRequestResponse(content='',
                                                          headers=headers)
        response = views.metadataview(self.request,
                                      'fakecontainer',
                                      'fakeobject')

        self.assertIn('fake/object', response.content)

    @patch('swiftbrowser.views.actionlog.log')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.put_container')
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

    @patch('swiftbrowser.views.actionlog.log')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.put_container')
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

    @patch('swiftbrowser.views.actionlog.log')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.put_container')
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

    @patch('swiftbrowser.views.actionlog.log')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.delete_container')
    @patch('swiftbrowser.views.client.head_container')
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

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.delete_container')
    @patch('swiftbrowser.views.client.head_container')
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
        self.assertEqual(msgs[0].message, 'Access denied.')

        self.assertEqual(mock_logging.call_count, 1)

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.delete_container')
    @patch('swiftbrowser.views.client.head_container')
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
        self.assertEqual(msgs[0].message, 'Access denied.')

        self.assertEqual(mock_logging.call_count, 1)

    @patch('swiftbrowser.views.render_to_response')
    @patch('swiftbrowser.views.client.head_container')
    def test_object_versioning_view_versioning_disabled(self,
                                                        mock_head_container,
                                                        mock_render):
        mock_head_container.return_value = {}

        views.object_versioning(self.request, 'fakecontainer')

        kargs = mock_render.mock_calls[0][2]
        computed = kargs.get('dictionary')

        expected = {'objects': utils.generic_pagination([], 1),
                    'container': 'fakecontainer',
                    'version_location': None}

        self.assertEqual(str(computed['objects']), str(expected['objects']))
        self.assertEqual(computed['container'], expected['container'])
        self.assertEqual(computed['version_location'], expected['version_location'])

    @patch('swiftbrowser.views.render_to_response')
    @patch('swiftbrowser.views.client.get_container')
    @patch('swiftbrowser.views.client.head_container')
    def test_object_versioning_view_versioning_enabled(self,
                                                       mock_head_container,
                                                       mock_get_container,
                                                       mock_render):
        mock_head_container.return_value = {'x-versions-location': 'abc'}
        mock_get_container.return_value = (None, [])

        views.object_versioning(self.request, 'fakecontainer')

        kargs = mock_render.mock_calls[0][2]
        computed = kargs.get('dictionary')

        expected = {'objects': utils.generic_pagination([], 1),
                    'container': 'fakecontainer',
                    'version_location': 'abc'}

        self.assertEqual(str(computed['objects']), str(expected['objects']))
        self.assertEqual(computed['container'], expected['container'])
        self.assertEqual(computed['version_location'], expected['version_location'])

    @patch('swiftbrowser.views.enable_versioning')
    def test_object_versioning_view_enabling_versioning(self, mock_enable):

        post = self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'action': 'enable'})
        self.request.POST = post

        response = views.object_versioning(self.request, 'fakecontainer')

        self.assertEqual(mock_enable.call_count, 1)

        location = response.items()[1][1]
        expected = reverse('object_versioning',
                           kwargs={'container': 'fakecontainer'})

        self.assertEqual(location, expected)

    @patch('swiftbrowser.views.disable_versioning')
    def test_object_versioning_view_disabling_versioning(self, mock_disable):

        post = self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'action': 'disable'})
        self.request.POST = post

        response = views.object_versioning(self.request, 'fakecontainer')

        self.assertEqual(mock_disable.call_count, 1)

        location = response.items()[1][1]
        expected = reverse('object_versioning',
                           kwargs={'container': 'fakecontainer'})

        self.assertEqual(location, expected)


class TestSwiftbrowserAcls(TestCase):

    def setUp(self):

        self.user = fakes.FakeUser(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated = lambda: True
        self.request = fake_request(user=self.user)

    def tearDown(self):
        patch.stopall()

    def test_edit_acl_needs_authentication(self):
        """ Verify if views.edit_acl is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.edit_acl(self.request)

        self.assertEqual(response.status_code, 302)

    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_list_acls_container_publico(self, mock_get_container):
        """
            Verify the ACL list for a container public and
            if the "Make private" action is available
        """
        mock_get_container.return_value = {
            'x-container-read': '.r:*',
            'x-container-write': '',
        }

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Add ACL to container fakecontainer', response.content)
        self.assertIn('Make private', response.content)
        self.assertIn('Add ACL', response.content)
        self.assertIn('.r:*', response.content)

    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_list_acls_container_private(self, mock_get_container):
        """
            Verify the ACL list for a private container with no ACLS and
            if the "Make Public" action is available
        """
        mock_get_container.return_value = {
            'x-container-read': '',
            'x-container-write': '',
        }

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Make public', response.content)
        self.assertIn('Add ACL', response.content)

        expected = 'There are no ACLs for this container yet. Add a new ACL by clicking the red button.'
        self.assertIn(expected, response.content)

    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_container_privado_mas_publico_para_leitura_e_escrita_para_um_user_e_project(self, mock_head_container):
        """
            Verify if it's properly listing container's acl and
            if the "Make Public" action is available
        """
        mock_head_container.return_value = {
            'x-container-read': 'projectfake:userfake',
            'x-container-write': 'projectfake:userfake',
        }

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Make public', response.content)
        self.assertIn('Add ACL', response.content)
        self.assertIn('projectfake:userfake', response.content)

    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_container_publico_e_publico_para_leitura_para_mais_de_um_user_e_project(self, mock_head_container):
        """
            Verify if it's properly listing container's acl for a public container
            and if Make Private is available
        """
        mock_head_container.return_value = {
            'x-container-read': '.r:*,projectfake:userfake',
            'x-container-write': 'projectfake2:userfake2',
        }

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Make private', response.content)
        self.assertIn('Add ACL', response.content)
        self.assertIn('projectfake:userfake', response.content)
        self.assertIn('projectfake2:userfake2', response.content)

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
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

        response = views.edit_acl(self.request, 'fakecontainer')

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': ',projectfake:userfake',
            'X-Container-Read': ',projectfake:userfake'
        }
        self.assertEqual(expected_arg, kargs['headers'])

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].message, 'ACLs updated')

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
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

        response = views.edit_acl(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(msgs), 1)
        self.assertTrue(mock_logging.called)
        self.assertEqual(msgs[0].message, 'ACL update failed')

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
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

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_post_container.called)

        name, args, kargs = mock_post_container.mock_calls[0]
        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2,',
            'X-Container-Read': 'projectfake:userfake,'
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
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

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_post_container.called)

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2',
            'X-Container-Read': 'projectfake:userfake,.r:*'
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
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

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2,',
            'X-Container-Read': '.r:*,'
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
    def test_edit_acl_delete_acl_for_user_in_a_private_container(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-read': 'projectfake:userfake',
            'x-container-write': 'projectfake:userfake,projectfake2:userfake2',
        }

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': 'projectfake:userfake'})
        self.request.GET = get

        response = views.edit_acl(self.request, 'fakecontainer')

        self.assertEqual(response.status_code, 200)

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {
            'X-Container-Write': 'projectfake2:userfake2,',
            'X-Container-Read': ''
        }
        self.assertEqual(expected_arg, kargs['headers'])

    @patch('swiftbrowser.views.log.exception')
    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
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

        response = views.edit_acl(self.request, 'fakecontainer')

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(len(msgs), 1)
        self.assertTrue(mock_logging.called)
        self.assertEqual(msgs[0].message, 'ACL update failed.')
        self.assertIn('projectfake:userfake', response.content)


class TestSwiftbrowserCORS(TestCase):

    def setUp(self):

        self.user = fakes.FakeUser(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated = lambda: True
        self.request = fake_request(user=self.user)

        patch('swiftbrowser.views.actionlog',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_edit_cors_needs_authentication(self):
        """ Verify if views.edit_cors is requiring a authentication """
        self.user.is_authenticated = lambda: False
        response = views.edit_cors(self.request)

        self.assertEqual(response.status_code, 302)

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
    def test_define_novo_host_para_regra_de_cors_no_container(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-meta-access-control-allow-origin': '',
        }

        self.request.method = 'POST'
        post = self.request.POST.copy()

        post.update({'host': 'globo.com'})
        self.request.POST = post

        response = views.edit_cors(self.request, 'fakecontainer')

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {'x-container-meta-access-control-allow-origin': 'globo.com'}

        self.assertEqual(expected_arg, kargs['headers'])

    @patch('swiftbrowser.views.client.post_container')
    @patch('swiftbrowser.views.client.head_container')
    def test_remove_host_da_regra_de_cors_do_container(self, mock_head_container, mock_post_container):
        mock_head_container.return_value = {
            'x-container-meta-access-control-allow-origin': 'globo.com globoi.com',
        }

        self.request.method = 'GET'
        get = self.request.GET.copy()

        get.update({'delete': 'globo.com'})
        self.request.GET = get

        response = views.edit_cors(self.request, 'fakecontainer')

        name, args, kargs = mock_post_container.mock_calls[0]

        expected_arg = {'x-container-meta-access-control-allow-origin': 'globoi.com'}

        self.assertEqual(expected_arg, kargs['headers'])
