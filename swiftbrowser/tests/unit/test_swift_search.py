# -*- coding: utf-8 -*-

import requests
import json

from mock import patch, Mock
from unittest import TestCase
from django.utils.translation import activate

from swiftclient import client
from swiftbrowser.utils import requests
from alf.client import Client

from swiftbrowser.tests import fakes
from swiftbrowser import views

from vault.tests.fakes import fake_request


class TestSwiftSearch(TestCase):

    def setUp(self):
        self.user = fakes.FakeUser(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated.value = True
        self.request = fake_request(user=self.user)
        self.project_id = "1ad2d06a38c643fb8550fe35b0ef579a_test"
        self.container = "container_test"

        # silence log
        patch('swiftbrowser.views.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone',
              Mock(return_value=None)).start()

        # does not connect to the keystone client
        patch('keystoneclient.v2_0.client.Client').start()

    def tearDown(self):
        patch.stopall()

    def test_optin_container_status_needs_authentication(self):
        self.user.is_authenticated.value = False
        response = views.optin_container_status(self.request, self.container)

        self.assertEqual(response.status_code, 302)

    def test_config_optin_container_needs_authentication(self):
        self.user.is_authenticated.value = False
        response = views.config_optin_container(self.request, self.container)

        self.assertEqual(response.status_code, 302)

    @patch.object(requests, 'get')
    @patch.object(Client, 'get')
    def test_search_metadata_object_needs_authentication(self, mock_client, mock_requests):
        class ResponseMockClient(object):
            status_code = 200

            def json(self):
                return {
                    "hits": {"hits": [{"_id": "1", "_source": {"object": "object_test"}}]}
                }

        class ResponseMockRequests(object):
            headers = {
                'content-length': '147',
                'content-type': 'application/json; charset=utf-8'
            }

        mock_client.return_value = ResponseMockClient()
        mock_requests.return_value = ResponseMockRequests()

        self.user.is_authenticated.value = False
        response = views.search_metadata_object(self.request, self.project_id, self.container)

        self.assertEqual(response.status_code, 302)

    @patch('swiftbrowser.views.client.put_container')
    def test_config_optin_container_status_sucess(self, mock_put_container):
        mock_put_container.return_value = fakes.FakeRequestResponse(200, content=None, headers=None)
        self.request.method = 'GET'

        get = self.request.GET.copy()
        get.update({'status': 'enabled'})
        get.update({'optin': 'false'})

        self.request.GET = get

        response = views.config_optin_container(self.request, self.container)

        self.assertEqual(response.status_code, 200)

        expected = 'ativada'
        self.assertIn(expected, response.content)

    @patch('swiftbrowser.views.client.put_container')
    def test_config_optin_container_fail(self, mock_put_container):
        mock_put_container.side_effect = client.ClientException('')
        self.request.method = 'GET'

        get = self.request.GET.copy()
        get.update({'status': 'enabled'})
        get.update({'optin': 'false'})

        self.request.GET = get

        response = views.config_optin_container(self.request, self.container)

        self.assertEqual(response.status_code, 500)

        expected = 'Failed to enable search'
        self.assertIn(expected, response.content)

    @patch('swiftbrowser.views.client.head_container')
    def test_optin_container_status_work_fine(self, mock_head_container):
        mock_head_container.return_value = {'x-container-meta-enqueue': 'False'}

        response = views.optin_container_status(self.request, self.container)

        self.assertEqual(response.status_code, 200)

        expected = '{"status": "disabled"}'
        self.assertIn(expected, response.content)

    @patch('swiftbrowser.views.client.head_container')
    def test_optin_container_status_fail(self, mock_head_container):
        mock_head_container.side_effect = client.ClientException('')

        response = views.optin_container_status(self.request, self.container)

        self.assertEqual(response.status_code, 500)

        expected = 'Error on head_container'
        self.assertIn(expected, response.content)

    @patch.object(requests, 'get')
    @patch.object(Client, 'get')
    @patch('swiftbrowser.views.client.get_container')
    def test_search_metadata_object_work_fine(self, mock_get_container, mock_client, mock_requests):
        class ResponseMockClient(object):
            status_code = 200

            def json(self):
                return {
                    "hits": {"hits": [{"_id": "1", "_source": {"object": "object_test"}}]}
                }

        class ResponseMockRequests(object):
            headers = {
                'content-length': '147',
                'content-type': 'application/json; charset=utf-8'
            }

        mock_client.return_value = ResponseMockClient()
        mock_requests.return_value = ResponseMockRequests()
        mock_get_container.return_value = {'x-container-meta-enqueue': 'True'}, []

        self.request.method = 'GET'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        get = self.request.GET.copy()
        get.update({'query': 'test'})

        self.request.GET = get

        response = views.search_metadata_object(self.request, self.project_id, self.container)

        self.assertEqual(response.status_code, 200)

        expected = 'DOCTYPE'
        self.assertIn(expected, response.content)

    @patch.object(requests, 'get')
    @patch.object(Client, 'get')
    @patch('swiftbrowser.utils.get_backstage_client')
    @patch('swiftbrowser.views.client.get_container')
    def test_search_metadata_object_fail(self, mock_get_container, mock_bs_client, mock_client, mock_requests):
        class ResponseMockClient(object):
            status_code = 200

            def json(self):
                return {
                    "hits": {"hits": [{"_id": "1", "_source": {"object": "object_test"}}]}
                }

        class ResponseMockRequests(object):
            headers = {
                'content-length': '147',
                'content-type': 'application/json; charset=utf-8'
            }

        mock_client.return_value = ResponseMockClient()
        mock_requests.return_value = ResponseMockRequests()
        mock_bs_client.return_value = {"hits": {"hits": [{"object": "object_test"}]}}
        mock_get_container.side_effect = client.ClientException('')

        self.request.method = 'GET'

        get = self.request.GET.copy()
        get.update({'query': 'test'})

        self.request.GET = get

        response = views.search_metadata_object(self.request, self.project_id, self.container)

        self.assertEqual(response.status_code, 302)

        self.assertIn('', response.content)

    @patch.object(requests, 'get')
    @patch.object(Client, 'get')
    @patch('swiftbrowser.utils.get_backstage_client')
    @patch('swiftbrowser.views.client.get_container')
    def test_search_metadata_object_with_blank_input(self, mock_get_container, mock_bs_client, mock_client, mock_requests):
        class ResponseMockClient(object):
            status_code = 200

            def json(self):
                return {
                    "hits": {"hits": [{"_id": "1", "_source": {"object": "object_test"}}]}
                }

        class ResponseMockRequests(object):
            headers = {
                'content-length': '147',
                'content-type': 'application/json; charset=utf-8'
            }

        mock_client.return_value = ResponseMockClient()
        mock_requests.return_value = ResponseMockRequests()
        mock_bs_client.return_value = {"hits": {"hits": [{"object": "object_test"}]}}
        mock_get_container.return_value = {'x-container-meta-enqueue': 'True'}, []
        activate('en-us')
        self.request.method = 'GET'
        self.request.META.update({
            'HTTP_HOST': 'localhost'
        })
        get = self.request.GET.copy()

        self.request.GET = get

        response = views.search_metadata_object(self.request, self.project_id, self.container)

        self.assertEqual(response.status_code, 200)

        self.assertIn('', response.content)

        msgs = [msg for msg in self.request._messages]

        self.assertEqual(msgs[0].message, 'Please fill the field for search!')
