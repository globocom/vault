# -*- coding: utf-8 -*-

from django.db import models


class BackupContainer(models.Model):
    id = models.AutoField(primary_key=True)
    container = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'swift_backup_container'
        unique_together = ('container', 'project_id',)

    def __unicode__(self):
        return "Container: {}, Project: {}".format(self.container,
                                                   self.project_name)
