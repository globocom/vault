# -*- coding:utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView
from keystoneclient.openstack.common.apiclient import exceptions

from swiftclient import client

from identity.keystone import Keystone
from vault.views import LoginRequiredMixin
from vault.models import GroupProjects
from swiftbrowser.utils import get_admin_url


log = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def __init__(self, *args, **kwargs):
        self.keystone = None
        return super(DashboardView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        # context['widget_users_data'] = self._widget_users()
        # context['widget_storage_data'] = self._widget_storage()

        return context

    # def _widget_users(self):
    #     users = []

    #     try:
    #         users = self.keystone.user_list()
    #     except exceptions.Forbidden:
    #         return False
    #     except Exception as e:
    #         log.exception('Exception: %s' % e)
    #         messages.add_message(self.request, messages.ERROR,
    #                              "Error getting user list")
    #     return {
    #         'total_users': len(users),
    #         'url': reverse('users')
    #     }

    # def _widget_storage(self):
    #     storage_url = get_admin_url(self.request)
    #     auth_token = self.request.user.token.id
    #     http_conn = client.http_connection(storage_url,
    #                                        insecure=settings.SWIFT_INSECURE)
    #     try:
    #         account_stat, containers = client.get_account(storage_url,
    #                                                       auth_token,
    #                                                       http_conn=http_conn)
    #     except client.ClientException as err:
    #         log.exception('Exception: {0}'.format(err))
    #         return False
    #         # TODO - Handle user without permission
    #         # messages.add_message(self.request, messages.ERROR,
    #         #                     'Unable to list containers')
    #         containers = []

    #     objects = 0
    #     size = 0

    #     for container in containers:
    #         objects += container['count']
    #         size += container['bytes']

    #     return {
    #         'containers': len(containers),
    #         'objects': objects,
    #         'size': size,
    #         'url': reverse('containerview')
    #     }
