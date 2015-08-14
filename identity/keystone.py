# -*- coding:utf-8 -*-
import random
import string

import logging

from django.conf import settings
from django.views.decorators.debug import sensitive_variables
from keystoneclient.v2_0 import client

from vault.models import GroupProjects, Project, AreaProjects


log = logging.getLogger(__name__)


class UnauthorizedProject(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
         return repr(self.value)


class Keystone(object):
    """ return an authenticated keystone client """

    def __init__(self, request, tenant_name=None):
        self.token = request.session.get('token', None)

        if tenant_name:
            self.tenant_name = tenant_name
        else:
            self.tenant_name = getattr(settings, 'PROJECT_BOLADAO')

        project = Project.objects.get(name=self.tenant_name)
        groups = request.user.groups.all()

        # Talvez nao seja o melhor local para esta verificacao
        group_projects = GroupProjects.objects.filter(group__in=groups,
                                                      project_id=project.id)

        # Pode autenticar se project pertence ao time do usuario, ou o usuario
        # eh superuser
        if not group_projects and not request.user.is_superuser:
            raise UnauthorizedProject('Usuario sem permissao neste project')

        self.conn = self._keystone_conn(request)

    def _keystone_conn(self, request):

        kwargs = {
            'remote_addr': request.environ.get('REMOTE_ADDR', ''),
            'auth_url': getattr(settings, 'KEYSTONE_URL'),
            'insecure': True,
            'tenant_name': self.tenant_name,
        }

        if self.token:
            kwargs['token'] = self.token
        else:
            kwargs['username'] = getattr(settings, 'USERNAME_BOLADAO')
            kwargs['password'] = getattr(settings, 'PASSWORD_BOLADAO')

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

    def user_list(self, project=None):
        return self.conn.users.list(project)

    def user_get(self, user_id):
        user = self.conn.users.get(user_id)
        return self._user_manager(user)

    @sensitive_variables('password')
    def user_create(self, name=None, email=None, password=None,
                    project=None, enabled=None, domain=None, role=None):

        if settings.KEYSTONE_VERSION < 3:
            user = self.conn.users.create(name, password, email, project, enabled)
        else:
            user = self.conn.users.create(name, password=password, email=email,
                                  project=project, enabled=enabled, domain=domain)

        # Assign role and project to user
        if project is not None and role is not None:
            role = self.role_get(role)
            project = self.project_get(project)

            # V2 a role '_member_' eh vinculada automaticamente
            if settings.KEYSTONE_VERSION > 2 or role.name != '_member_':
                self.add_user_role(user, project, role)

        return user

    @sensitive_variables('password')
    def user_update(self, user, **data):

        if settings.KEYSTONE_VERSION < 3:
            password = data.pop('password')
            project = data.pop('project')

            user = self.conn.users.update(user, **data)

            if password:
                self.user_update_password(user, password)
        else:
            # Se senha for /False/, retira do dicionario para nao atualizar com /False/
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

    def project_update(self, project, **data):
        conn = self._project_manager()

        if settings.KEYSTONE_VERSION < 3:
            return conn.update(project.id, data['name'], data['description'], data['enabled'])
        else:
            return conn.update(project, **data)

    def project_delete(self, project_id):
        conn = self._project_manager()
        return conn.delete(project_id)

    def project_list(self):
        conn = self._project_manager()

        if self.user.is_superuser:
            return conn.list()
        else:
            return conn.list(user=self.user.id)

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

    def vault_create_project(self, name, group_id, area_id, description=None,
                             enabled=True,):
        """
        Metodo que faz o processo completo de criacao de project no vault:
        Cria projeta, cria um usuario, e vincula com a role swiftoperator
        """
        project = self.project_create(name, description=description,
                                      enabled=enabled)

        user_password = Keystone.create_password()

        user = self.user_create(name='u_{}'.format(name),
                                password=user_password,
                                role=settings.ROLE_BOLADONA,
                                project=project.id)

        # Salva o project no time correspondente
        gp = GroupProjects(group=group_id, project=project.id)
        gp.save()

        # Salva o project na area correspondente
        ap = AreaProjects(area=area_id, project=project.id)
        ap.save()

    @staticmethod
    def create_password():
        caracteres = string.ascii_letters + string.digits + '!@#$%&*_'
        return ''.join(random.choice(caracteres) for x in range(12))