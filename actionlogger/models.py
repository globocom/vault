# -*- coding:utf-8 -*-

from django.db import models
import datetime

class Audit(models.Model):
    user = models.CharField(max_length=30) 	     		 # WHO
    action = models.CharField(max_length=30)     		 # WHAT
    item = models.CharField(max_length=30)	     		 # WHERE
    created_at = models.DateField(auto_now_add=True)	 # WHEN	

    def __unicode__(self):
        return " %s - %s - %s - %s " % (self.user, self.action, self.item, self.created_at)
