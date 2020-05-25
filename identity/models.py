# -*- coding: utf-8 -*-

from django.db import models


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'
        unique_together = (('project'),)
