# -*- coding: utf-8 -*-

from mock import patch
from unittest import TestCase

from actionlogger import ActionLogger, ActionNotFound


class TestActionLogger(TestCase):

    def setUp(self):
        self.actionlog = ActionLogger()

    @patch("actionlogger.syslog.syslog")
    def test_logging_an_action(self, syslog_mock):
        self.actionlog.log('TestUser', 'create', 'A Test Project')
        syslog_mock.assert_called_with(6, "User TestUser Criou A Test Project")

    def test_log_with_an_invalid_action_raises_actionnotfound(self):
        self.assertRaises(ActionNotFound, self.actionlog.log,
                          'TestUser', 'drop', 'A Test Project')
