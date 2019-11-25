# -*- coding: utf-8 -*-

from mock import patch, Mock
from unittest import TestCase

from swiftbrowser.tests import fakes
from swiftbrowser.views import backup

from vault.tests.fakes import fake_request


class TestSwiftBackup(TestCase):

    def setUp(self):
        self.user = fakes.FakeUser(42, 'user')
        self.user.is_authenticated.value = True
        self.request = fake_request(user=self.user)

        # silence log
        patch('swiftbrowser.views.backup.log',
              Mock(return_value=None)).start()

    def tearDown(self):
        patch.stopall()

    def test_authenticated_config_backup_url(self):
        self.user.is_authenticated.value = False
        response = backup.config_backup_container(self.request, 'blah')

        self.assertEqual(response.status_code, 302)
