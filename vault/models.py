# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext as _
from django.db.models.signals import class_prepared


# Vault
class GroupProjects(models.Model):

    group = models.ForeignKey(Group)
    project = models.CharField(max_length=255)
    owner = models.BooleanField(default=0)

    class Meta:
        db_table = 'group_projects'
        unique_together = (('group', 'project'),)
        verbose_name_plural = _('Teams and Projects')

    def __unicode__(self):
        return "Team {} - Project {}".format(self.group, self.project)


class CurrentProject(models.Model):

    user = models.OneToOneField(User)
    project = models.CharField(max_length=255)

    class Meta:
        db_table = 'current_project'
        verbose_name_plural = _('Current Project')


class OG(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(max_length=255)

    class Meta:
        db_table = 'og'
        verbose_name = _('OG')
        verbose_name_plural = _('OGs')

    def __unicode__(self):
        return " %s" % (self.name)


class TeamOG(models.Model):

    group = models.ForeignKey(Group)
    og = models.ForeignKey(OG)

    class Meta:
        db_table = 'team_og'
        unique_together = (('group'),)
        verbose_name_plural = _('Team and OG')
