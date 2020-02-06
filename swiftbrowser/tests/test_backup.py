# -*- coding: utf-8 -*-

from unittest.mock import patch, Mock
from unittest import TestCase

from swiftbrowser.tests import fakes
from swiftbrowser.views import backup

from vault.tests.fakes import fake_request


class TestSwiftBackup(TestCase):

    def setUp(self):
        self.request = fake_request(user=False)

        # silence log
        patch('swiftbrowser.views.backup.log',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_authenticated_config_backup_url(self):
        response = backup.config_backup_container(self.request, 'blah')

        self.assertEqual(response.status_code, 302)
