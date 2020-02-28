# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from swiftclient import client as swclient

from dashboard.widgets import BaseWidget
from storage.utils import get_storage_endpoint


log = logging.getLogger(__name__)


class SwiftWidget(BaseWidget):
    widget_template = 'storage/widgets/swift.html'

    def get_widget_context(self):
        request = self.context.get("request")
        storage_url = get_storage_endpoint(request, 'adminURL')

        if storage_url is None:
            return {}

        auth_token = request.session.get('auth_token')
        http_conn = swclient.http_connection(storage_url,
                                             insecure=settings.SWIFT_INSECURE)
        try:
            head_acc = swclient.head_account(storage_url,
                                             auth_token,
                                             http_conn=http_conn)
        except Exception as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR,
                                 _('Unable to show Swift info'))
            return {}

        return {
            'containers': head_acc.get('x-account-container-count'),
            'objects': head_acc.get('x-account-object-count'),
            'size': head_acc.get('x-account-bytes-used'),
            'info': {
                'project': request.session.get("project_name"),
                'endpoints': {
                    'adminURL': storage_url,
                    'publicURL': get_storage_endpoint(request, 'publicURL'),
                    'internalURL': get_storage_endpoint(request, 'internalURL')
                }
            }
        }

    @property
    def is_visible(self):
        project_id = self.context.get('project_id')
        if project_id is None:
            return False
        return True
