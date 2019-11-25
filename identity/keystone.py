# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.utils.translation import ugettext as _

from storm_keystone.keystone import Keystone as KeystoneBase

from vault.models import GroupProjects


log = logging.getLogger(__name__)

vault_db = settings.DATABASES.get('default')
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(vault_db.get('USER'),
                                                 vault_db.get('PASSWORD'),
                                                 vault_db.get('HOST'),
                                                 vault_db.get('PORT'),
                                                 vault_db.get('NAME'))
BASE_CONFIG = {
    'KEYSTONE_TENANT': settings.KEYSTONE_PROJECT,
    'KEYSTONE_USERNAME': settings.KEYSTONE_USERNAME,
    'KEYSTONE_PASSWORD': settings.KEYSTONE_PASSWORD,
    'KEYSTONE_URL': settings.KEYSTONE_URL,
    'KEYSTONE_VERSION': settings.KEYSTONE_VERSION,
    'KEYSTONE_ROLE_ID': settings.KEYSTONE_ROLE,
    'SQLALCHEMY_DATABASE_URI': DB_URI,
    'DICIONARIO_URL': settings.CUSTEIO_DICIONARIO_URL,
}


class KeystoneNoRequest(KeystoneBase):

    def __init__(self, username=None, password=None, tenant_name=None):
        return super(KeystoneNoRequest, self).__init__(username, password,
                                                       tenant_name,
                                                       config=BASE_CONFIG)


class Keystone(KeystoneBase):

    def __init__(self, request=None, username=None, password=None,
                 tenant_name=None):
        self.request = request
        super(Keystone, self).__init__(username, password, tenant_name,
                                       config=BASE_CONFIG)

    def extra_config(self):
        return {
            'remote_addr': self.request.environ.get('REMOTE_ADDR', ''),
            'insecure': True,
        }

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
