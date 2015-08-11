# -*- coding:utf-8 -*-

from mock import patch
from unittest import TestCase
from actionlogger.models import *
from actionlogger import ActionLogger, ActionNotFound

import datetime

audit = Audit(user='TestUser', action='create', item='A Test Project')   

class TestActionLogger(TestCase):

	def setUp(self):
		self.actionlog = ActionLogger()

	@patch("actionlogger.syslog.syslog")
	def test_logging_an_action(self, syslog_mock):
		self.actionlog.log('TestUser', 'create', 'A Test Project')
		syslog_mock.assert_called_with(6, "User (TestUser) CREATED: A Test Project")

	def test_log_with_an_invalid_action_raises_actionnotfound(self):
		self.assertRaises(ActionNotFound, self.actionlog.log,
                          'TestUser', 'drop', 'A Test Project')

	def test_audit_action(self):
		self.actionlog.savedb(audit)
		line = Audit.objects.get(id=audit.id)        
		self.assertEqual(line.user,'TestUser')
