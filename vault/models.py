# -*- coding:utf-8 -*-

from django.db import models

class Area(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=30)
	description = models.TextField(max_length=255)
	created_at = models.DateField(auto_now=True)

	class Meta:
		db_table = 'vault_area'

	def __unicode__(self):
		return " %s - %s - %s - %s " % (self.user, self.action, self.item, self.created_at)
