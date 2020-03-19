# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import class_prepared


class GroupProjects(models.Model):

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    project = models.CharField(max_length=255)
    owner = models.BooleanField(default=0)

    class Meta:
        db_table = 'group_projects'
        unique_together = (('group', 'project'),)
        verbose_name_plural = _('Groups and Projects')

    def __str__(self):
        return "Group {} - Project {}".format(self.group, self.project)


class CurrentProject(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.CharField(max_length=255)

    class Meta:
        db_table = 'current_project'
        verbose_name_plural = _('Current Project')
