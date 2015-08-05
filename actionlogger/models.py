# -*- coding:utf-8 -*-

from django.db import models

class Audit(models.Model):
	id = models.AutoField(primary_key=True)
	user = models.CharField(max_length=30)
	action = models.CharField(max_length=30)
	item = models.CharField(max_length=30)
	created_at = models.DateField(auto_now_add=True)

	def __unicode__(self):
		return " %s - %s - %s - %s " % (self.user, self.action, self.item, self.created_at)
