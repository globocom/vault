# -*- coding:utf-8 -*-


from django.db import models
import datetime


class Audit(models.Model):
    NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=60, null=False, blank=False)
    action = models.CharField(max_length=60, null=False, blank=False)
    item = models.TextField(max_length=255, null=False, blank=False)
    through = models.TextField(max_length=255, default='vault')
    created_at = models.DateTimeField(auto_now=True, default=NOW)

    class Meta:
        db_table = 'vault_audit'

    def __unicode__(self):
        return " %s - %s - %s - %s " % (self.user, self.action, self.item, self.created_at)
