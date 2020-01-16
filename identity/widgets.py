# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext as _

from swiftclient import client as swclient

from dashboard.widgets import BaseWidget


log = logging.getLogger(__name__)


class KeystoneWidget(BaseWidget, WithKeystoneMixin):
    widget_template = 'identity/widgets/keystone.html'

    def get_widget_context(self):
        return {
        }

    @property
    def is_visible(self):
        user = self.context.get('user')
        print(user.is_superuser)
        return user.is_superuser
