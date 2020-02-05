# -*- coding: utf-8 -*-

import json

from unittest.mock import patch, Mock
from unittest import TestCase

from swiftclient import client

from swiftbrowser.tests import fakes
from swiftbrowser import views

from vault.tests.fakes import fake_request


class TestSwiftAcl(TestCase):
    """
    Class to test methods related to setting a container public/private
    through Vault interface (containerview)
    """

    def setUp(self):
        self.request = fake_request()
        self.project_id = "1ad2d06a38c643fb8550fe35b0ef579a_test"
        self.container = "container_test"

        # silence log
        patch('swiftbrowser.views.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_container_acl_update_needs_authentication(self):
        req = fake_request(user=False)
        response = views.container_acl_update(req, self.container)

        self.assertEqual(response.status_code, 302)

    def test_container_acl_status_needs_authentication(self):
        req = fake_request(user=False)
        response = views.container_acl_status(req, self.container)

        self.assertEqual(response.status_code, 302)

    @patch('swiftbrowser.views.client.head_container')
    def test_container_acl_status(self, mock_head_container):
        # Private container
        mock_head_container.return_value = {}
        response = views.container_acl_status(self.request, self.container)
        computed = json.loads(response.content)

        self.assertEqual(computed['status'], 'disabled')

        # Public container
        mock_head_container.return_value = {'x-container-read': '.r:*'}
        response = views.container_acl_status(self.request, self.container)
        computed = json.loads(response.content)

        self.assertEqual(computed['status'], 'enabled')

    @patch('swiftbrowser.views.client.head_container')
    @patch('swiftbrowser.views.client.post_container')
    def test_container_acl_update_set_to_private(self, mock_post, mock_head):
        mock_head.return_value = {}

        self.request.method = 'GET'
        _get = self.request.GET.copy()
        _get.update({'status': 'disabled'})
        self.request.GET = _get

        response = views.container_acl_update(self.request, self.container)

        # Check header POST to the container
        computed_headers = mock_post.call_args[1].get('headers')
        self.assertEqual(computed_headers['x-container-read'], '')

    @patch('swiftbrowser.views.client.head_container')
    @patch('swiftbrowser.views.client.post_container')
    def test_container_acl_update_set_to_public(self, mock_post, mock_head):
        mock_head.return_value = {}

        self.request.method = 'GET'
        _get = self.request.GET.copy()
        _get.update({'status': 'enabled'})
        self.request.GET = _get

        response = views.container_acl_update(self.request, self.container)

        # Check header POST to the container
        computed_headers = mock_post.call_args[1].get('headers')
        self.assertEqual(computed_headers['x-container-read'], '.r:*')
