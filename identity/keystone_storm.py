import random
import string
import logging

import requests
import keystoneclient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
try:
    from keystoneclient.openstack.common.apiclient import exceptions
except ModuleNotFoundError as e:
    from keystoneclient import exceptions

from storm_keystone.models import Base, User, UserGroup, Group, GroupProject


logging.basicConfig()
log = logging.getLogger(__name__)


class Keystone(object):
    """Returns an authenticated keystone client"""

    def __init__(self, username=None, password=None, tenant_name=None,
                 auth_url=None, db_uri=None, config={}):

        db_uri = db_uri if db_uri else config.get('SQLALCHEMY_DATABASE_URI')
        tenant = tenant_name if tenant_name else config.get('KEYSTONE_TENANT')
        username = username if username else config.get('KEYSTONE_USERNAME')
        password = password if password else config.get('KEYSTONE_PASSWORD')
        auth_url = auth_url if auth_url else config.get('KEYSTONE_URL')

        self.config = {
            'version': config.get('KEYSTONE_VERSION', 2),
            'timeout': config.get('KEYSTONE_TIMEOUT', 3),
            'role_id': config.get('KEYSTONE_ROLE_ID'),

            'auth_url': auth_url,
            'username': username,
            'password': password,
            'tenant_name': tenant,
            'db_uri': db_uri,
        }

        self.config.update(self.extra_config())

        # keystone connection
        self.conn = None
        if self.allow_connection():
            self.conn = self._create_keystone_connection()

        # db connection
        self.Session = self._create_db_session()

    def extra_config(self):
        return {}

    def allow_connection(self):
        return True

    def _create_keystone_connection(self):
        if self.config['version'] < 3:
            client = keystoneclient.v2_0.client
        else:
            client = keystoneclient.v3.client

        return client.Client(**self.config)

    def _create_db_session(self):
        engine = create_engine(self.config.get('db_uri'), pool_recycle=240)

        Base.metadata.create_all(engine)
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def vault_group_project_delete(self, project_id):
        session = self.Session()
        session.query(GroupProject).filter_by(project=project_id).delete()
        session.commit()

    def vault_group_project_create(self, group_id, project_id, owner=0):
        session = self.Session()
        group_project = GroupProject(group_id=group_id,
                                     project=project_id,
                                     owner=owner)
        session.add(group_project)
        session.commit()
        return group_project

    def vault_user_get(self, user_id):
        session = self.Session()
        return session.query(User).get(user_id)

    def vault_user_get_by_name(self, username):
        session = self.Session()
        return session.query(User).filter_by(username=username).first()

    def vault_user_list(self):
        session = self.Session()
        return session.query(User).all()

    def vault_user_group_get(self, user_id):
        session = self.Session()
        return session.query(UserGroup).filter_by(user_id=user_id).one()

    def vault_user_group_list(self, user_id):
        session = self.Session()
        return session.query(UserGroup).filter_by(user_id=user_id).all()

    def vault_group_get_by_name(self, name):
        session = self.Session()
        return session.query(Group).filter(Group.name.ilike(name)).one()

    # based on: https://github.com/openstack/horizon/blob/master/openstack_dashboard/api/keystone.py#L51-L56
    def _project_manager(self):
        if self.config['version'] < 3:
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

    def user_create(self, name, email=None, password=None, enabled=True,
                    domain=None, project_id=None, role_id=None):

        if self.config['version'] < 3:
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

            # V2 the '_member_' role is automatically linked
            # if self.config['version'] > 2 or role.name != '_member_':
            self.add_user_role(user, project, role)

        return user

    def user_update(self, user, **data):
        if self.config['version'] < 3:
            password = data.pop('password')

            user = self.conn.users.update(user, **data)

            if password:
                self.user_update_password(user, password)
        else:
            # If password is /False/, removes it to not update with /False/
            if not data['password']:
                data.pop('password')

            user = self.conn.users.update(user, **data)

        return user

    def user_update_password(self, user, password):
        if self.config['version'] < 3:
            return self.conn.users.update_password(user, password)
        else:
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

        if self.config['version'] < 3:
            return conn.create(name, description, enabled, **kwargs)
        else:
            return conn.create(name, domain_id, description=description,
                               enabled=enabled, **kwargs)

    def project_update(self, project, **kwargs):
        conn = self._project_manager()

        if self.config['version'] < 3:
            return conn.update(project.id, **kwargs)
        else:
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

    def add_user_role(self, user=None, project=None, role=None):
        if self.config['version'] < 3:
            return self.conn.roles.add_user_role(user, role, project)
        else:
            return self.conn.roles.grant(role, user=user, project=project)

    def remove_user_role(self, user=None, project=None, role=None):
        if self.config['version'] < 3:
            return self.conn.roles.remove_user_role(user, role, project)
        else:
            return self.conn.roles.revoke(role, user=user, project=project)

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
        except exceptions.Conflict:
            return {
                'status': False,
                'reason': 'Duplicated project name.'
            }
        except exceptions.Forbidden:
            return {
                'status': False,
                'reason': 'Superuser required.'
            }

        # Creates user and add swiftoperator role
        try:
            user_password = Keystone.create_password()
            user = self.user_create(name='u_{}'.format(project_name),
                                    password=user_password,
                                    role_id=self.config['role_id'],
                                    project_id=project.id)
        except exceptions.Forbidden:
            self.project_delete(project.id)
            return {
                'status': False,
                'reason': 'Admin required'
            }

        # Link the project to a team
        try:
            self.vault_group_project_create(group_id=group_id,
                                            project_id=project.id,
                                            owner=1)
        except Exception:
            self.project_delete(project.id)
            self.user_delete(user.id)
            return {
                'status': False,
                'reason': 'Unable to assign project to group'
            }

        return {
            'status': True,
            'project': project,
            'user': user,
            'password': user_password
        }

    def vault_set_project_owner(self, project_id, group_id):
        session = self.Session()
        current = (session.query(GroupProject)
                                .filter_by(project=project_id, owner=1)
                                .first())

        if current and int(current.group_id) == int(group_id):
            return {
                'status': False,
                'reason': 'Group already owner'
            }

        if current:
            current.owner = 0
            session.add(current)

        new = (session.query(GroupProject)
                      .filter_by(project=project_id, group_id=group_id, owner=0)
                      .first())
        if new:
            new.owner = 1
            session.add(new)
        else:
            self.vault_group_project_create(group_id, project_id, 1)

        session.commit()

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

        # user = self.return_find_u_user(project.id)
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
        user = self.return_find_u_user(project.id)
        if user:
            self.user_delete(user.id)

        # Delete group_project
        self.vault_group_project_delete(project.id)

        # Delete from business_service_project
        self.vault_business_service_project_delete(project.id)

        # Delete from Keystone
        try:
            self.project_delete(project.id)
        except Exception as err:
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

    def return_find_u_user(self, project_id):
        """
        Metodo que recebe o id do project e busca o usuario que tenha o nome
        u_<project_name> e retorna este usuario.
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
        sc_endpoints = self.conn.service_catalog.get_endpoints()
        endpoints = {}

        for service, i in sc_endpoints.items():
            item = i[0]
            service_name = service.replace('-', '_')
            endpoints[service_name] = {
                'adminURL': item.get('adminURL'),
                'publicURL': item.get('publicURL'),
                'internalURL': item.get('internalURL')
            }
        return endpoints

    def get_object_store_endpoints(self):
        endpoints = self.get_endpoints()
        return endpoints.get('object_store')
