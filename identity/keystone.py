# -*- coding: utf-8 -*-

import random
import string
import logging
import requests

from keystoneclient import exceptions, v3

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group

from vault.models import GroupProjects
from identity.models import Project


log = logging.getLogger(__name__)


class KeystoneBase:

    def __init__(self, username=None, password=None, project_name=None,
                 auth_url=None, config={}):

        self.config = {
            'version': 3,
            'timeout': settings.KEYSTONE_TIMEOUT,

            'auth_url': auth_url or settings.KEYSTONE_URL,
            'username': username or settings.KEYSTONE_USERNAME,
            'password': password or settings.KEYSTONE_PASSWORD,
            'project_name': project_name or settings.KEYSTONE_PROJECT,
        }

        self.config.update(config)

        # keystone connection
        self.conn = None
        if self.allow_connection():
            self.conn = self._create_keystone_connection()

    def allow_connection(self):
        return True

    def _create_keystone_connection(self):
        client = v3.client

        return client.Client(**self.config)

    def vault_database_project_delete(self, project_id):
        project = Project.objects.filter(project=project_id)
        project.delete()

    def vault_group_project_delete(self, project_id):
        group_projects = GroupProjects.objects.filter(project=project_id)
        group_projects.delete()

    def vault_group_project_create(self, group_id, project_id, owner=0):
        group_project = GroupProjects(group_id=group_id,
                                      project=project_id,
                                      owner=owner)
        group_project.save()
        return group_project

    def vault_user_get(self, user_id):
        return User.objects.get(id=user_id)

    def vault_user_get_by_name(self, username):
        return User.objects.get(username=username)

    def vault_user_list(self):
        return User.objects.all()

    def vault_user_group_get(self, user_id, group_id):
        return User.objects.get(id=user_id, groups__id=group_id)

    def vault_user_group_list(self, user_id):
        return Group.objects.filter(user__id=user_id)

    def vault_group_get_by_name(self, name):
        return Group.objects.get(name=name)

    # based on: https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/keystone.py#L51-L56
    def _project_manager(self):
        return self.conn.projects

    # based on: https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/keystone.py#L45-L49
    def _user_manager(self, user):
        if getattr(user, "default_project_id", None) is None:
            user.project_id = getattr(user, "tenantId", None)
        return user

    def user_list(self, project_id=None):
        """
        List project users. If no project is defined, it will list all users.

        :param project_id: string or None
        :return: list
        :raises: NotFound if project does not exists
        """
        return self.conn.users.list(project_id)

    def user_get(self, user_id):
        user = self.conn.users.get(user_id)
        return self._user_manager(user)

    def user_create(self, name, email=None, password=None, enabled=True,
                    domain=None, project_id=None, role_id=None):

        user = self.conn.users.create(name, password=password, email=email,
                                      project=project_id, enabled=enabled,
                                      domain=domain)

        # Assign role and project to user
        if project_id is not None and role_id is not None:
            role = self.role_get(role_id)
            project = self.project_get(project_id)

            # V2 the '_member_' role is automatically linked
            # if self.config['version'] > 2 or role.name != '_member_':
            self.add_user_role(user, project, role)

        return user

    def user_update(self, user, **data):
        # If password is /False/, removes it to not update with /False/
        if not data['password']:
            data.pop('password')

        user = self.conn.users.update(user, **data)

        return user

    def user_update_password(self, user, password):
        return self.conn.users.update(user, password=password)

    def user_delete(self, user_id):
        return self.conn.users.delete(user_id)

    def user_get_by_name(self, user_name):
        users = self.user_list()

        for user in users:
            if user.name == user_name:
                return user

        return None

    def user_update_enabled(self, user_id, enabled=False):
        return self.conn.users.update_enabled(user_id, enabled)

    def project_create(self, name, domain_id='default', description=None,
                       enabled=True, **kwargs):
        conn = self._project_manager()

        return conn.create(name, domain_id, description=description,
                           enabled=enabled, **kwargs)

    def project_update(self, project, **kwargs):
        conn = self._project_manager()

        return conn.update(project, **kwargs)

    def project_delete(self, project_id):
        conn = self._project_manager()
        return conn.delete(project_id)

    def project_update_enabled(self, project_id, enabled=False):
        project = self.project_get(project_id)
        return project.update(enabled=enabled)

    def project_list(self):
        conn = self._project_manager()
        return conn.list()

    def project_get(self, project_id):
        conn = self._project_manager()
        return conn.get(project_id)

    def project_get_by_name(self, project_name):
        projects = self.project_list()

        for project in projects:
            if project.name == project_name:
                return project

        return None

    def role_list(self):
        return self.conn.roles.list()

    def role_get(self, role_id):
        return self.conn.roles.get(role_id)

    def role_find(self, name):
        return self.conn.roles.find(name=name)

    def list_user_roles(self, user=None, project=None):
        roleManager = v3.roles.RoleManager(self.conn)
        return roleManager.list(user=user, project=project)

    def add_user_role(self, user=None, project=None, role=None):
        return self.conn.roles.grant(role, user=user, project=project)

    def remove_user_role(self, user=None, project=None, role=None):
        return self.conn.roles.revoke(role, user=user, project=project)

    def role_assignments_list(self, user=None, group=None, project=None, domain=None, role=None):
        return self.conn.role_assignments.list(
            user=user, group=group, project=project, domain=domain, role=role)

    def vault_project_create(self, project_name, group_id, description=None,
                             **kwargs):
        """
        This method do the complete project create process:
            - Creates project
            - creates user
            - add swiftoperator role
            - link the project to a team
        """

        # Creates project
        try:
            project = self.project_create(project_name,
                                          description=description,
                                          enabled=True,
                                          **kwargs)
        except exceptions.Conflict as err:
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': 'Duplicated project name.'
            }
        except exceptions.Forbidden as err:
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': 'Superuser required.'
            }

        swiftop = settings.KEYSTONE_ROLE or \
                  self.conn.roles.find(name='swiftoperator').id
        # Creates admin user and add swiftoperator role
        try:
            admin_password = Keystone.create_password()
            admin_user = self.user_create(
                name='u_{}'.format(project_name),
                password=admin_password,
                role_id=swiftop,
                project_id=project.id
            )
        except exceptions.Forbidden as err:
            self.project_delete(project.id)
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': 'Admin User required'
            }

        # Creates internal user and add swiftoperator role
        try:
            user_name = 'u_vault_{}'.format(project_name)
            internal_password = Keystone.create_password()
            internal_user = self.user_create(
                name=user_name,
                email=self.request.user.email,
                password=internal_password,
                project_id=project.id,
                enabled=project.enabled,
                domain=project.domain_id,
                role_id=swiftop
            )
        except exceptions.Forbidden as err:
            self.user_delete(admin_user.id)
            self.project_delete(project.id)
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': 'Internal User required'
            }

        # Creates project user
        try:
            from vault.utils import encrypt_password
            password = encrypt_password(internal_password)
            db_project = Project(
                project=project.id,
                user=user_name,
                password=password.decode("utf-8")
            )
            db_project.save()
        except Exception as err:
            self.user_delete(admin_user.id)
            self.user_delete(internal_user.id)
            self.project_delete(project.id)
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': 'Project User required'
            }

        # Link the project to a team
        try:
            self.vault_group_project_create(group_id=group_id,
                                            project_id=project.id,
                                            owner=1)
        except Exception as err:
            self.user_delete(admin_user.id)
            self.user_delete(internal_user.id)
            self.project_delete(project.id)
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': 'Unable to assign project to group'
            }

        return {
            'status': True,
            'project': project,
            'user': admin_user,
            'password': admin_password
        }

    def vault_set_project_owner(self, project_id, group_id):
        current = (GroupProjects.objects.filter(project=project_id, owner=1)
                                        .first())

        if current and int(current.group_id) == int(group_id):
            return {
                'status': False,
                'reason': 'Group already owner'
            }

        if current:
            current.owner = 0

        new = (GroupProjects.objects.filter(project=project_id,
                                            group_id=group_id,
                                            owner=0)
                                    .first())
        if new:
            new.owner = 1
        else:
            self.vault_group_project_create(group_id, project_id, 1)

        current.save()
        new.save()

        return {
            'status': True
        }

    def vault_project_update(self, project_id, project_name, group_id,
                             **kwargs):
        project = self.project_get(project_id)
        try:
            updated_project = self.project_update(project,
                                                  name=project_name,
                                                  **kwargs)
        except exceptions.Forbidden:
            return {
                'status': False,
                'reason': 'Admin required'
            }

        if group_id is not None:
            self.vault_set_project_owner(project_id, group_id)

        return {
            'status': True,
            'project': updated_project
        }

    def vault_project_delete(self, project_name):
        """
        Delete project and the "u_<project_name>" user.
        """

        project = self.project_get_by_name(project_name)
        if not project:
            return {
                'status': False,
                'reason': 'Project not found'
            }

        # This is the code that disables project and user
        # intead of delete them
        # try:
        #     project = self.project_update_enabled(project.id, False)
        # except Exception as err:
        #     return {
        #         'status': False,
        #         'reason': err
        #     }

        # user = self.find_user_with_u_prefix(project.id, 'u')
        # if user:
        #     self.user_update_enabled(user.id, False)

        # Delete from Swift
        del_swift = self._project_delete_swift(project.id)

        # Swift returns 404 if the project had never been used
        if del_swift.status_code not in (204, 404):
            reason = 'Unable to delete project from Swift (HTTP {})'.format(
                del_swift.status_code)

            return {
                'status': False,
                'reason': reason
            }

        # Delete user named "u_<project_name>"
        user = self.find_user_with_u_prefix(project.id, 'u')
        if user:
            self.user_delete(user.id)

        # Delete user named "u_vault_<project_name>"
        user = self.find_user_with_u_prefix(project.id, 'u_vault')
        if user:
            self.user_delete(user.id)

        # Delete project from vault database
        self.vault_database_project_delete(project.id)

        # Delete group_project
        self.vault_group_project_delete(project.id)

        # Delete from Keystone
        try:
            self.project_delete(project.id)
        except Exception as err:
            log.error('Error: {}'.format(err))
            return {
                'status': False,
                'reason': err
            }

        return {
            'status': True
        }

    def _project_delete_swift(self, project_id):

        headers = {
            'X-Storage-Token': self.conn.auth_token
        }
        verify = not self.config.get('insecure')

        # replace project_id in url to the id of the project that will
        # be deleted
        storage_url = self.get_object_store_endpoints()['adminURL']
        _, project_admin_id = storage_url.split('AUTH_')
        url = storage_url.replace(project_admin_id, project_id)

        return requests.delete(url, headers=headers, verify=verify)

    def find_user_with_u_prefix(self, project_id, prefix):
        project = self.project_get(project_id)
        users = self.user_list(project.id)

        for user in users:
            if user.name == '{}_{}'.format(prefix, project.name):
                return user

        return None

    @staticmethod
    def create_password():
        caracteres = string.ascii_letters + string.digits + '!@#$%&*_'
        return ''.join(random.choice(caracteres) for x in range(12))

    def get_endpoints(self):
        sc_endpoints = self.conn.service_catalog.get_endpoints()
        endpoints = {}

        for service, item in sc_endpoints.items():
            service_name = service.replace('-', '_')
            endpoints[service_name] = {
                a['interface'] + 'URL': a['url'] for a in item
            }
        return endpoints

    def get_object_store_endpoints(self):
        endpoints = self.get_endpoints()
        return endpoints.get('object_store')


class KeystoneNoRequest(KeystoneBase):

    def __init__(self, username=None, password=None, project_name=None,
                 auth_url=None):
        return super(KeystoneNoRequest, self).__init__(username, password,
                                                       project_name, auth_url)


class Keystone(KeystoneBase):

    def __init__(self, request=None, username=None, password=None,
                 project_name=None, auth_url=None):

        self.request = request
        extra_config = {
            'remote_addr': self.request.environ.get('REMOTE_ADDR', ''),
            'insecure': False,
        }

        super(Keystone, self).__init__(username, password, project_name,
                                       auth_url, config=extra_config)

    def allow_connection(self):
        return self._is_allowed_to_connect()

    def _is_allowed_to_connect(self):
        """
        Check if logged user can access the project set on session.
        If no project was set, it means that it should connect to the "admin"
        project.
        """

        project_id = self.request.session.get('project_id')
        groups = self.request.user.groups.all()
        group_projects = []

        if project_id:
            group_projects = GroupProjects.objects.filter(group__in=groups,
                                                          project=project_id)
        else:
            # caso nao exista project_id no ambiente, preciso
            # verificar o caso de um usuario num grupo recem-criado
            # sem projeto definido
            group_projects = GroupProjects.objects.filter(group__in=groups)
            if not group_projects and not project_id:
                return True

        # Pode autenticar se project pertence ao time do usuario
        if not group_projects and not self.request.user.is_superuser:
            log.warning(_('Permission denied to manage this project'))
            return False

        return True
