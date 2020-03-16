# -*- coding: utf-8 -*-
from django.db import models


class Audit(models.Model):

    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=60, null=True, blank=True)
    action = models.CharField(max_length=60, null=True, blank=True)
    item = models.TextField(max_length=255, null=True, blank=True)
    through = models.TextField(max_length=255, default='vault')
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'audit'

    def __str__(self):
        return "{} - {} - {} - {}".format(self.user, self.action, self.item, self.created_at)
