import os
import unittest
import mock

from vault import settings


class SettingsTestCase(unittest.TestCase):

    def setUp(self):
        self.original_environ = os.environ

    def tearDown(self):
        os.environ = self.original_environ

    def test_get_settings_path_default_is_local(self):
        os.environ = {}
        response = settings.get_settings_path()
        expected = "vault.settings.local"
        self.assertEqual(response, expected)

    def test_get_settings_path_from_environment_variable(self):
        os.environ = {"ENVIRON": "abc"}
        response = settings.get_settings_path()
        expected = "vault.settings.abc"
        self.assertEqual(response, expected)

    def test_load_module_attributes(self):
        sample_module_path = "vault.tests.unit.dummy_settings"
        settings.load_module_attributes(sample_module_path)
        response = settings.the_best_team
        expected = 'STORM'
        self.assertEqual(response, expected)
