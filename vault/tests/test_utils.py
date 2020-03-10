# -*- coding: utf-8 -*-

"""
Unit tests for utils functions
"""

import datetime

from unittest import TestCase
from unittest.mock import patch

from keystoneclient.v3.projects import Project

from vault import utils
from vault.models import CurrentProject
from django.core.paginator import PageNotAnInteger, EmptyPage
from vault.tests.fakes import fake_request, UserFactory


class TestVaultUtils(TestCase):

    def setUp(self):
        # does not connect to the keystone client
        patch('keystoneclient.v3.client.Client').start()

    def tearDown(self):
        patch.stopall()

    def test_generic_pagination(self):
        items = [1, 2, 3, 4, 5, 6]

        # First page
        paginated_items = utils.generic_pagination(items, 1, 2)
        computed = [k for k in paginated_items]
        expected = [1, 2]
        self.assertEqual(computed, expected)
        self.assertFalse(paginated_items.has_previous())
        self.assertTrue(paginated_items.has_next())

        # Second page
        paginated_items = utils.generic_pagination(items, 2, 2)
        computed = [k for k in paginated_items]
        expected = [3, 4]
        self.assertEqual(computed, expected)
        self.assertTrue(paginated_items.has_previous())
        self.assertTrue(paginated_items.has_next())

        # Last page
        paginated_items = utils.generic_pagination(items, 3, 2)
        computed = [k for k in paginated_items]
        expected = [5, 6]
        self.assertEqual(computed, expected)
        self.assertTrue(paginated_items.has_previous())
        self.assertFalse(paginated_items.has_next())

        # If page bigger than the last page, always return last page
        paginated_items = utils.generic_pagination(items, 4, 2)
        computed = [k for k in paginated_items]
        expected = [5, 6]
        self.assertEqual(computed, expected)

    @patch('django.core.paginator.Paginator')
    def test_generic_pagination_return_except_emptypage(self, mock_paginator):
        mock_paginator.side_effect = EmptyPage()

        items = [1, 2, 3, 4, 5, 6]

        paginated_items = utils.generic_pagination(items, 1, 2)

        self.assertEqual(paginated_items.next_page_number(), 2)

    @patch('django.core.paginator.Paginator')
    def test_generic_pagination_return_except_pagenotinteger(self, mock_paginator):
        mock_paginator.side_effect = PageNotAnInteger()

        items = [1, 2, 3, 4, 5, 6]

        paginated_items = utils.generic_pagination(items, 1, 2)

        self.assertEqual(paginated_items.number, 1)

    @patch('identity.keystone.KeystoneNoRequest.project_get_by_name')
    def test_set_current_project(self, mock_project):
        project = Project('123', {})
        project.id = 1
        project.name = 'Teste'

        mock_project.return_value = project

        request = fake_request(method='GET')
        request.user = UserFactory(id='999', username='u_user_test')
        patch('identity.keystone.Keystone._create_keystone_connection').start()

        project_name = request.session['project_name']
        utils.set_current_project(request, project)

        self.assertEqual(request.session['project_id'], 1)
        self.assertEqual(request.session['project_name'], 'Teste')

    @patch('vault.models.CurrentProject.objects.get')
    @patch('identity.keystone.KeystoneNoRequest.project_get')
    def test_get_current_project(self, mock_project, mock_current_project):
        mock_current_project.return_value = CurrentProject()

        project = Project('123', {})
        project.id = 1
        project.name = 'Nome'

        mock_project.return_value = project

        result_project = utils.get_current_project('1')

        self.assertEqual(result_project.id, project.id)
        self.assertEqual(result_project.name, project.name)

    @patch('vault.models.CurrentProject.objects.get')
    def test_get_current_project_return_none(self, mock_current_project):
        mock_current_project.side_effect = CurrentProject.DoesNotExist()

        result_project = utils.get_current_project('1')

        self.assertEqual(result_project, None)

    @patch('identity.keystone.Keystone._create_keystone_connection')
    def test_maybe_update_token_without_time_token_value(self, keystone_conn_mock):
        conn_mock = keystone_conn_mock.return_value
        conn_mock.auth_token = '12345678'

        request = fake_request(method='GET')
        request.session['token_time'] = None
        result = utils.maybe_update_token(request)

        self.assertTrue(result)

    @patch('identity.keystone.Keystone._create_keystone_connection')
    def test_maybe_update_token_with_expired_time_token(self, keystone_conn_mock):
        conn_mock = keystone_conn_mock.return_value
        conn_mock.auth_token = '12345678'

        request = fake_request(method='GET')
        expired_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=16)
        request.session['token_time'] = expired_time
        result = utils.maybe_update_token(request)

        self.assertTrue(result)

    @patch('identity.keystone.Keystone._create_keystone_connection')
    def test_maybe_update_token_with_valid_time_token(self, keystone_conn_mock):
        conn_mock = keystone_conn_mock.return_value
        conn_mock.auth_token = '12345678'

        request = fake_request(method='GET')
        valid_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        request.session['token_time'] = valid_time
        result = utils.maybe_update_token(request)

        self.assertFalse(result)
