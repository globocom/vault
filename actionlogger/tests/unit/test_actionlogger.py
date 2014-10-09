# -*- coding:utf-8 -*-

import os
import logging
from unittest import TestCase

from actionlogger import ActionLogger, ActionNotFound


class TestActionLogger(TestCase):

    def setUp(self):
        self.actionlog = ActionLogger('test_actions.log')

    @classmethod
    def tearDownClass(cls):
        os.remove('test_actions.log')

    def test_actionlogger_create_a_file_handler(self):
        self.assertTrue(os.path.isfile('test_actions.log'))

    def test_logging_an_action(self):
        self.actionlog.log('TestUser', 'create', 'A Test Project')

        logfile = open('test_actions.log', 'r')
        content = logfile.read()
        logfile.close()

        self.assertIn('User (TestUser) CREATED: A Test Project', content)

    def test_log_with_an_invalid_action_raises_actionnotfound(self):
        self.assertRaises(ActionNotFound, self.actionlog.log,
                          'TestUser', 'drop', 'A Test Project')
