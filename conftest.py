# -*- coding: utf-8 -*-

import sys
import os
import django


def pytest_sessionstart():
    sys.path.insert(0, os.path.dirname(__file__) + '/vault')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'vault.settings'
    django.setup()
