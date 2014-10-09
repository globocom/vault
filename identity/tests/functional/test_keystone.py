# -*- coding:utf-8 -*-

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

    def test_user_create_no_project(self):
        """ create user with basic informations """

        self.user = self.keystone.user_create(name='test_user_create_no_project',
            email='test_user_create_no_project@email.com',
            password='asd9)SHda2b19bajk',
            enabled=False)

        self.assertEqual(self.user.name, 'test_user_create_no_project')
        self.assertEqual(self.user.email, 'test_user_create_no_project@email.com')
        self.assertFalse(self.user.enabled)

    def test_user_create_complete(self):
        """ create user with all informations """

        role_list = self.keystone.role_list()
        role = role_list.pop()
        # Pra V2, a role _member_ eh relacionado automaticamente
        # Buscamos outra role, caso o pop tenha retirado essa role
        if role.name == '_member_':
            if len(role_list) > 1:
                role = role_list.pop()
            else:
                role = None

        project_list = self.keystone.project_list()
        project = project_list.pop()

        self.user = self.keystone.user_create(name='test_user_create',
            email='test_user_create@email.com',
            password='asd9)SHda2b19bajk',
            enabled=False,
            project=project.id,
            role=role.id)

        self.assertEqual(self.user.name, 'test_user_create')
        self.assertEqual(self.user.email, 'test_user_create@email.com')
        self.assertEqual(self.user.tenantId, project.id)
        self.assertFalse(self.user.enabled)

    def test_user_update(self):

        self.user = self.keystone.user_create(name='test_user_update',
            email='test_user_update@email.com',
            password='asd9SHda2b19bajk',
            enabled=False)

        self.user = self.keystone.user_update(self.user,
                                    name='test_user_update_updated',
                                    email='test_user_update_updated@email.com',
                                    password=None,
                                    project=None,
                                    enabled=True)

        self.assertEqual(self.user.name, 'test_user_update_updated')
        self.assertEqual(self.user.email, 'test_user_update_updated@email.com')
        self.assertTrue(self.user.enabled)

    def test_user_update_password(self):
        self.user = self.keystone.user_create(name='test_user_update_password',
            email='test_user_update_password@email.com',
            password='asd9SHda2b19bajk',
            enabled=False)

        res = self.keystone.user_update_password(self.user, 'kajdljsdiasodia')

        # TODO: Not sure if this is enough to test password updade
        self.assertEqual(res.name, self.user.name)
        self.assertEqual(res.email, self.user.email)

    def test_user_delete(self):
        self.user = self.keystone.user_create(name='test_user_delete',
            email='test_user_delete@email.com',
            password='asd9SHda2b19bajk',
            enabled=False)

        (response, dev_null) = self.keystone.user_delete(self.user.id)
        self.assertEqual(response.status_code, 204)

        # Avoid delete on tearDown
        if response.status_code == 204:
            self.user = None

    def test_add_user_role(self):

        role_list = self.keystone.role_list()
        role = role_list.pop()

        project_list = self.keystone.project_list()
        project = project_list.pop()

        self.user = self.keystone.user_create(name='test_add_user_role',
            email='test_add_user_role@email.com',
            password='asd9SHda2b19bajk',
            enabled=False)

        role_added = self.keystone.add_user_role(user=self.user, project=project, role=role)

        # busca as roles atuais do user
        current_roles = self.user.list_roles(project.id)

        self.assertEqual(len(current_roles), 1)
        self.assertEqual(current_roles[0].id, role.id)

    def test_remove_user_role(self):

        role_list = self.keystone.role_list()
        role = role_list.pop()
        # Pra V2, a role _member_ eh relacionado automaticamente
        # Buscamos outra role, caso o pop tenha retirado essa role
        if role.name == '_member_':
            if len(role_list) > 1:
                role = role_list.pop()
            else:
                role = None

        project_list = self.keystone.project_list()
        project = project_list.pop()

        self.user = self.keystone.user_create(name='test_remove_user_role',
            email='test_remove_user_role@email.com',
            password='asd9SHda2b19bajk',
            enabled=False,
            project=project.id,
            role=role.id)

        (response, dev_null) = self.keystone.remove_user_role(user=self.user, project=project, role=role)

        self.assertEqual(response.status_code, 204)

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


class TestKeystoneV2(TestCase, KeystoneBase):

    def setUp(self):

        settings.OPENSTACK_API_VERSIONS = {
            "identity": 2
        }

        cli = Client()
        response = cli.post('/auth/login/', {
            'username': 'admin',
            'password': 'admin',
            'region': settings.OPENSTACK_KEYSTONE_URL
        })

        self.request = fake_request()
        self.request.user.token = FakeToken(cli.session['token'].id)
        self.request.user.service_catalog = cli.session['token'].serviceCatalog
        self.request.user.is_superuser = True

        self.keystone = Keystone(self.request)

        self.project = None
        self.user = None

    def tearDown(self):
        if self.project is not None:
            self.project.delete()

        if self.user is not None:
            self.user.delete()

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
