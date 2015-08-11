# -*- coding:utf-8 -*-

import logging

from django.conf import settings
from django.views.decorators.debug import sensitive_variables

from vault.models import GroupProjects

# Mapping of V3 Catalog Endpoint_type to V2 Catalog Interfaces
ENDPOINT_TYPE_TO_INTERFACE = {
    'public': 'publicURL',
    'internal': 'internalURL',
    'admin': 'adminURL',
}

if settings.KEYSTONE_VERSION == 3:
    from keystoneclient.v3 import client
else:
    from keystoneclient.v2_0 import client


log = logging.getLogger(__name__)


class UnauthorizedProject(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
         return repr(self.value)


class Keystone(object):
    """ return an authenticated keystone client """

    def __init__(self, request, tenant_id=None):
        self.token = request.session.get('token', None)
        self.tenant_id = tenant_id

        self.conn = self._keystone_conn(request)

        # Talvez nao seja o melhor local para esta verificacao
        groups = request.user.groups.all()
        group_projects = GroupProjects.objects.filter(group__in=groups,
                                                      project_id=self.tenant_id)

        if not group_projects and not request.user.is_superuser:
            raise UnauthorizedProject('Usuario sem permissao neste project')


    def _keystone_conn(self, request):

        kwargs = {
            'remote_addr': request.environ.get('REMOTE_ADDR', ''),
            'endpoint': getattr(settings, 'OPENSTACK_KEYSTONE_URL'),
            'auth_url': getattr(settings, 'OPENSTACK_KEYSTONE_URL'),
            'insecure': getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False),
            'cacert': getattr(settings, 'OPENSTACK_SSL_CACERT', None),
        }

        if self.tenant_id:
            kwargs['tenant_id'] = self.tenant_id

        if self.token:
            kwargs['token'] = self.token
        else:
            kwargs['username'] = getattr(settings, 'USERNAME_BOLADAO')
            kwargs['password'] = getattr(settings, 'PASSWORD_BOLADAO')

        conn = client.Client(**kwargs)

        return conn

    # def _get_keystone_endpoint(self):
    #     interface = 'internal'

    #     if self.user.is_superuser:
    #         interface = 'admin'

    #     service = self._get_service_from_catalog('identity')

    #     for endpoint in service['endpoints']:

    #         if settings.KEYSTONE_VERSION < 3:
    #             interface = ENDPOINT_TYPE_TO_INTERFACE.get(interface, '')

    #             return endpoint[interface]

    #         else:

    #             if endpoint['interface'] == interface:
    #                 return endpoint['url']

    def _get_service_from_catalog(self, service_type):
        catalog = self.user.service_catalog

        if catalog:
            for service in catalog:
                if service['type'] == service_type:
                    return service

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

    def project_create(self, request, name, domain_id='default',
                       description=None, enabled=True):
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
