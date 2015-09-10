# -*- coding: utf-8 -*-

import random
import string

from django.conf import settings
from django.views.decorators.debug import sensitive_variables
from keystoneclient.v2_0 import client
from keystoneclient.openstack.common.apiclient import exceptions

from vault.models import GroupProjects, Project, AreaProjects


class Keystone(object):
    """ return an authenticated keystone client """

    def __init__(self, request, username=None, password=None, tenant_name=None):
        self.request = request

        if username is not None and password is not None:
            self.username = username
            self.password = password
        else:
            self.username = getattr(settings, 'USERNAME_BOLADAO')
            self.password = getattr(settings, 'PASSWORD_BOLADAO')

        if tenant_name:
            self.tenant_name = tenant_name
        else:
            self.tenant_name = getattr(settings, 'PROJECT_BOLADAO')

        self.conn = self._keystone_conn(request)

    def _is_allowed_to_connect(self):

        project = Project.objects.get(name=self.tenant_name)
        groups = self.request.user.groups.all()

        group_projects = GroupProjects.objects.filter(group__in=groups,
                                                      project_id=project.id)

        # Pode autenticar se project pertence ao time do usuario, ou o usuario
        # eh superuser
        if not group_projects and not self.request.user.is_superuser:
            msg = 'Permission denied to list this project'
            raise exceptions.AuthorizationFailure(msg)

    def _keystone_conn(self, request):

        self._is_allowed_to_connect()

        kwargs = {
            'remote_addr': request.environ.get('REMOTE_ADDR', ''),
            'auth_url': getattr(settings, 'KEYSTONE_URL'),
            'insecure': True,
            'tenant_name': self.tenant_name,
            'username': self.username,
            'password': self.password,
            'timeout': 3,
        }

        conn = client.Client(**kwargs)

        return conn

    # based on: https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/keystone.py#L51-L56
    def _project_manager(self):
        if settings.KEYSTONE_VERSION < 3:
            return self.conn.tenants
        else:
            return self.conn.projects

    # based on: https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/keystone.py#L45-L49
    def _user_manager(self, user):
        if getattr(user, "project_id", None) is None:
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

    @sensitive_variables('password')
    def user_create(self, name, email=None, password=None, enabled=True,
                    domain=None, project_id=None, role_id=None):

        if settings.KEYSTONE_VERSION < 3:
            user = self.conn.users.create(name, password, email, project_id,
                                          enabled)
        else:
            user = self.conn.users.create(name, password=password, email=email,
                                          project=project_id, enabled=enabled,
                                          domain=domain)

        # Assign role and project to user
        if project_id is not None and role_id is not None:
            role = self.role_get(role_id)
            project = self.project_get(project_id)

            # V2 a role '_member_' eh vinculada automaticamente
            # if settings.KEYSTONE_VERSION > 2 or role.name != '_member_':
            self.add_user_role(user, project, role)

        return user

    @sensitive_variables('password')
    def user_update(self, user, **data):

        if settings.KEYSTONE_VERSION < 3:
            password = data.pop('password')
            # project = data.pop('project')

            user = self.conn.users.update(user, **data)

            if password:
                self.user_update_password(user, password)
        else:
            # Se senha for /False/, retira para nao atualizar com /False/
            if not data['password']:
                data.pop('password')

            user = self.conn.users.update(user, **data)

        return user

    @sensitive_variables('password')
    def user_update_password(self, user, password):
        if settings.KEYSTONE_VERSION < 3:
            return self.conn.users.update_password(user, password)
        else:
            return self.conn.users.update(user, password=password)

    def user_delete(self, user_id):
        return self.conn.users.delete(user_id)

    def project_create(self, name, domain_id='default', description=None,
                       enabled=True):
        conn = self._project_manager()

        if settings.KEYSTONE_VERSION < 3:
            return conn.create(name, description, enabled)
        else:
            return conn.create(name, domain_id,
                                description=description,
                                enabled=enabled)

    def project_update(self, project, **kwargs):
        conn = self._project_manager()

        if settings.KEYSTONE_VERSION < 3:
            return conn.update(project.id, kwargs['name'],
                               kwargs['description'], kwargs['enabled'])
        else:
            return conn.update(project, **kwargs)

    def project_delete(self, project_id):
        conn = self._project_manager()
        return conn.delete(project_id)

    def project_list(self):
        conn = self._project_manager()
        return conn.list()

    def project_get(self, project_id):
        conn = self._project_manager()
        return conn.get(project_id)

    def role_list(self):
        return self.conn.roles.list()

    def role_get(self, role_id):
        return self.conn.roles.get(role_id)

    def add_user_role(self, user=None, project=None, role=None):
        if settings.KEYSTONE_VERSION < 3:
            return self.conn.roles.add_user_role(user, role, project)
        else:
            return self.conn.roles.grant(role, user=user, project=project)

    def remove_user_role(self, user=None, project=None, role=None):
        if settings.KEYSTONE_VERSION < 3:
            return self.conn.roles.remove_user_role(user, role, project)
        else:
            return self.conn.roles.revoke(role, user=user, project=project)

    # TODO: Este metodo esta fazendo muitas operacoes. Avaliar refatoracao
    def vault_create_project(self, project_name, group_id, area_id,
                             description=None):
        """
        Metodo que faz o processo completo de criacao de project no vault:
        Cria projeto, cria um usuario, vincula com a role swiftoperator,
        associa a um time e associa a uma area.
        """
        try:
            project = self.project_create(project_name, description=description,
                                          enabled=True)
        except exceptions.Conflict:
            return {'status': False, 'reason': 'Duplicated project name.'}
        except exceptions.Forbidden:
            return {'status': False, 'reason': 'Superuser required.'}

        user_password = Keystone.create_password()

        try:
            user = self.user_create(name='u_{}'.format(project_name),
                                    password=user_password,
                                    role_id=settings.ROLE_BOLADONA,
                                    project_id=project.id)
        except exceptions.Forbidden:
            self.project_delete(project.id)
            return {'status': False, 'reason': 'Admin required'}

        try:
            # Salva o project no time correspondente
            gp = GroupProjects(group_id=group_id, project_id=project.id)
            gp.save()

        except Exception as e:
            self.project_delete(project.id)
            self.user_delete(user.id)
            return {
                'status': False,
                'reason': 'Unable to assign project to group'}

        # Salva o project na area correspondente
        try:
            ap = AreaProjects(area_id=area_id, project_id=project.id)
            ap.save()

        except Exception as e:
            self.project_delete(project.id)
            self.user_delete(user.id)
            return {
                'status': False,
                'reason': 'Unable to assign project to area'}

        return {
            'status': True,
            'project': project,
            'user': user,
            'password': user_password
        }

    def vault_update_project(self, project_id, project_name, group_id, area_id,
                             **kwargs):
        project = self.project_get(project_id)

        description = kwargs.get('description', '')
        enabled = kwargs.get('enabled', True)

        try:
            new_project = self.project_update(project,
                                              name=project_name,
                                              description=description,
                                              enabled=enabled)
        except exceptions.Forbidden:
            return {'status': False, 'reason': 'Admin required'}

        GroupProjects.objects.filter(project_id=project_id).delete()

        try:
            # Salva o project no time correspondente
            gp = GroupProjects(group_id=group_id, project_id=project_id)
            gp.save()
        except Exception as e:
            return {
                'status': False,
                'reason': 'Unable to assign project to group'}

        AreaProjects.objects.filter(project_id=project_id).delete()

        try:
            # Salva o project na area correspondente
            ap = AreaProjects(area_id=area_id, project_id=project_id)
            ap.save()
        except Exception as e:
            return {
                'status': False,
                'reason': 'Unable to assign project to group'}

        return {
            'status': True,
            'project': new_project,
        }

    def vault_delete_project(self, project_id):

        user = self.return_find_u_user(project_id)

        if user:
            self.user_delete(user.id)

        self.project_delete(project_id)

    def return_find_u_user(self, project_id):
        """
        Metodo que recebe o id do project e busca o usuario que tenha o nome u_<project_name>
        e retorna este usuario.
        """
        project = self.project_get(project_id)
        users = self.user_list(project.id)

        for user in users:
            if user.username == 'u_{}'.format(project.name):
                return user

    @staticmethod
    def create_password():
        caracteres = string.ascii_letters + string.digits + '!@#$%&*_'
        return ''.join(random.choice(caracteres) for x in range(12))

    def get_endpoints(self):

        service_catalog = self.conn.service_catalog
        urls = service_catalog.get_endpoints(service_type='object-store')

        return {
            'adminURL': urls['object-store'][0].get('adminURL'),
            'publicURL': urls['object-store'][0].get('publicURL'),
            'internalURL': urls['object-store'][0].get('internalURL'),
        }
