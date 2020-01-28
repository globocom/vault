# -*- coding: utf-8 -*-

import json

from unittest.mock import patch, Mock
from unittest import TestCase

from swiftclient import client

from swiftbrowser.tests import fakes
from swiftbrowser import views

from vault.tests.fakes import fake_request


class TestSwiftTrash(TestCase):

    def setUp(self):
        self.user = fakes.FakeUser(1, 'user')
        self.user.is_superuser = True
        self.user.is_authenticated.value = True
        self.request = fake_request(user=self.user)

        # silence log
        patch('swiftbrowser.views.log',
              Mock(return_value=None)).start()

        patch('identity.keystone.Keystone',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_deleted_objects_list_needs_authentication(self):
        self.user.is_authenticated.value = False
        response = views.get_deleted_objects(self.request)

        self.assertEqual(response.status_code, 302)

    @patch("swiftbrowser.views.client.get_container")
    def test_get_deleted_objects_returns_a_json(self, mock_get_container):
        mock_get_container.return_value = fakes.get_container()
        response = views.get_deleted_objects(self.request, 'container1')

        self.assertIn(b'application/json', response.serialize_headers())

    @patch("swiftbrowser.views.client.get_container")
    def test_check_properties_from_get_deleted_objects_content(self, mock_get_container):
        mock_get_container.return_value = fakes.get_container(trash_container=".trash-container1")

        response = views.get_deleted_objects(self.request, 'container1')
        expected_items = ["deleted_objects", "prefix", "storage_url",
                          "trash_container", "original_container"]

        result = json.loads(response.content)
        for item in expected_items:
            self.assertIn(item, result)

    @patch("swiftbrowser.views.client.get_container")
    def test_get_deleted_objects_client_exception(self, mock_get_container):
        mock_get_container.side_effect = client.ClientException("error message",
                                                                http_status=500)
        response = views.get_deleted_objects(self.request, 'container1')

        self.assertEqual(response.content, '{"error": "error message"}')
        self.assertEqual(response.status_code, 500)

    @patch("swiftbrowser.views.remove_from_trash")
    def test_deleted_objects_from_trash(self, mock_trash_remove):
        mock_trash_remove.return_value = fakes.FakeRequestResponse(200)

        response = views.remove_from_trash(self.request)

        self.assertEqual(response.status_code, 200)

    @patch("swiftbrowser.views.remove_from_trash")
    def test_deleted_objects_from_trash_with_fail(self, mock_trash_remove):
        mock_trash_remove.return_value = fakes.FakeRequestResponse(500)

        response = views.remove_from_trash(self.request)

        self.assertEqual(response.status_code, 500)

    @patch("swiftbrowser.views.delete_pseudofolder")
    def test_deleted_objects_from_pseudofolder(self, mock_remove_from_pseudo_folder):
        mock_remove_from_pseudo_folder.return_value = fakes.FakeRequestResponse(200)

        response = views.delete_pseudofolder(self.request, "container1", "pseudofolder")

        self.assertEqual(response.status_code, 200)

    @patch("swiftbrowser.views.delete_pseudofolder")
    def test_deleted_objects_from_pseudofolder_with_fail(self, mock_remove_from_pseudo_folder):
        mock_remove_from_pseudo_folder.return_value = fakes.FakeRequestResponse(500)

        response = views.delete_pseudofolder(self.request, "container1", "pseudofolder")

        self.assertEqual(response.status_code, 500)

    @patch("swiftbrowser.views.restore_object")
    def test_restore_object_from_trash(self, mock_restore):
        mock_restore.return_value = fakes.FakeRequestResponse(202)

        response = views.restore_object(self.request)

        self.assertEqual(response.status_code, 202)

    @patch("swiftbrowser.views.restore_object")
    def test_restore_object_from_trash_with_fail_error_on_put_object(self, mock_restore):

        mock_restore.return_value = fakes.FakeRequestResponse(500)

        response = views.restore_object(self.request)

        self.assertEqual(response.status_code, 500)

    @patch("swiftbrowser.views.restore_object")
    def test_restore_object_from_trash_with_fail_object_exists_on_container(self, mock_restore):

        mock_restore.return_value = fakes.FakeRequestResponse(409)

        response = views.restore_object(self.request)

        self.assertEqual(response.status_code, 409)
