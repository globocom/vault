# -*- coding:utf-8 -*-

from django.db import models

class Audit(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.CharField(max_length=30, null=False, blank=False)
	action = models.CharField(max_length=30, null=False, blank=False)
	item = models.CharField(max_length=30, null=False, blank=False)
	through = models.CharField(max_length=30,default='vault')
	created_at = models.DateField(auto_now=True)

	class Meta:
		db_table = 'vault_audit'

	def __unicode__(self):
		return " %s - %s - %s - %s " % (self.user, self.action, self.item, self.created_at)
