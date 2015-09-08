# -*- coding:utf-8 -*-

import os
from unittest import TestCase

from django.conf import settings
from identity.keystone import Keystone
from identity.tests.fakes import FakeToken
from vault.tests.fakes import fake_request

from django.test.client import Client


# class TestKeystoneV2(TestCase):
class KeystoneBase(object):
    """ Test keystone version 2 """

    def __init__(self):
        self.keystone = None
        self.request = None
        self.user = None
        self.project = None

    def test_user_list(self):
        user_list = self.keystone.user_list()
        user = user_list.pop()

        self.assertIn('list', str(type(user_list)))
        self.assertIn('User', str(type(user)))
        self.assertIsNotNone(user.name)
        self.assertIsNotNone(user.id)

    def test_role_list(self):
        role_list = self.keystone.role_list()
        role = role_list.pop()

        self.assertIn('list', str(type(role_list)))
        self.assertIn('Role', str(type(role)))
        self.assertIsNotNone(role.name)
        self.assertIsNotNone(role.id)

    def test_create_project(self):
        self.project = self.keystone.project_create(self.request,
                    'test_create_project',
                    description='desc project_teste',
                    enabled=False)

        self.assertEqual(self.project.name, 'test_create_project')
        self.assertEqual(self.project.description, 'desc project_teste')
        self.assertFalse(self.project.enabled)

    def test_update_project(self):
        self.project = self.keystone.project_create(self.request,
                    'test_update_project',
                    description='test_update_project',
                    enabled=True)

        self.assertEqual(self.project.name, 'test_update_project')

        self.project = self.keystone.project_update(self.project,
                        name='test_update_project_updated',
                        description='desc test_update_project_updated updated',
                        enabled=False)

        self.assertEqual(self.project.name, 'test_update_project_updated')
        self.assertEqual(self.project.description, 'desc test_update_project_updated updated')
        self.assertFalse(self.project.enabled)

    def test_project_delete(self):
        self.project = self.keystone.project_create(self.request,
                    'test_project_delete',
                    description='test_project_delete',
                    enabled=True)

        (response, dev_null) = self.keystone.project_delete(self.project.id)
        self.assertEqual(response.status_code, 204)

        # Avoid delete on tearDown
        if response.status_code == 204:
            self.project = None


# class TestKeystoneV2(TestCase, KeystoneBase):
#
#     def setUp(self):
#
#         settings.OPENSTACK_API_VERSIONS = {
#             "identity": 2
#         }
#
#         cli = Client()
#         response = cli.post('/auth/login/', {
#             'username': os.getenv('VAULT_TEST_USER'),
#             'password': os.getenv('VAULT_TEST_PASS'),
#             'region': settings.OPENSTACK_KEYSTONE_URL
#         })
#
#         self.request = fake_request()
#         self.request.user.token = FakeToken(cli.session['token'].id)
#         self.request.user.service_catalog = cli.session['token'].serviceCatalog
#         self.request.user.is_superuser = True
#
#         self.keystone = Keystone(self.request)
#
#         self.project = None
#         self.user = None
#
#     def tearDown(self):
#         if self.project is not None:
#             self.project.delete()
#
#         if self.user is not None:
#             self.user.delete()

# To teste Keystone V3, we need to update the endpoints urls
# class TestKeystoneV3(TestCase, KeystoneBase):

#     def setUp(self):

#         settings.OPENSTACK_API_VERSIONS = {
#             "identity": 3
#         }

#         cli = Client()
#         response = cli.post('/auth/login/', {
#             'username': 'admin',
#             'password': 'admin',
#             'region': settings.OPENSTACK_KEYSTONE_URL
#         })

#         self.request = fake_request()
#         self.request.user.token = FakeToken(cli.session['token'].id)
#         self.request.user.service_catalog = cli.session['token'].serviceCatalog
#         self.request.user.is_superuser = True

#         self.keystone = Keystone(self.request)

#         self.project = None
#         self.user = None

#     def tearDown(self):
#         if self.project is not None:
#             self.project.delete()

#         if self.user is not None:
#             self.user.delete()
