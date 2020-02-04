# -*- coding: utf-8 -*-

from unittest.mock import patch, Mock
from unittest import TestCase

from actionlogger.actionlogger import ActionLogger, ActionNotFound


class TestActionLogger(TestCase):

    def setUp(self):
        self.mock_audit = patch('actionlogger.actionlogger.Audit',
                                retun=Mock()).start()

        self.action_logger = ActionLogger()

    def tearDown(self):
        patch.stopall()

    def test_make_message(self):
        computed = self.action_logger._make_log_message(
            'User1', 'create', 'A Test Project')
        expected = 'Usuario User1 Criou A Test Project'

        self.assertEqual(computed, expected)

        computed = self.action_logger._make_log_message(
            'User2', 'update', 'A Test Project')
        expected = 'Usuario User2 Atualizou A Test Project'

        self.assertEqual(computed, expected)

    @patch('actionlogger.actionlogger.syslog.syslog')
    def test_log_invoke_syslog_info_level(self, mock):
        self.action_logger.log('User1', 'create', 'A Test Project')
        self.assertEqual(1, mock.call_count)
        mock.assert_called_with(6, 'Usuario User1 Criou A Test Project')

    @patch('actionlogger.actionlogger.Audit')
    def test_log_set_and_invoke_audit_model(self, audit_mock):
        save_mock = audit_mock.return_value.save
        save_mock.return_value = True
        self.action_logger.log('User1', 'create', 'A Test Project')
        self.assertEqual(1, save_mock.call_count)

    def test_log_with_an_invalid_action_raises_actionnotfound(self):
        self.assertRaises(ActionNotFound, self.action_logger.log,
                          'TestUser', 'drop', 'A Test Project')
