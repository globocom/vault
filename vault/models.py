from django.db import models
from django.contrib.auth.models import Group

# Keystone
class Domain(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(unique=True, max_length=64)
    enabled = models.IntegerField()
    extra = models.TextField(blank=True)

    class Meta:
        managed = False
        db_table = 'domain'


# Keystone
class Project(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    name = models.CharField(max_length=64)
    extra = models.TextField(blank=True)
    description = models.TextField(blank=True)
    enabled = models.IntegerField(blank=True, null=True)
    domain = models.ForeignKey(Domain)

    class Meta:
        managed = False
        db_table = 'project'


# Vault
class ProjectGroups(models.Model):
    project = models.ForeignKey(Project)
    group = models.ForeignKey(Group)

    class Meta:
        db_table = 'project_groups'
        unique_together = (('project', 'group'),)
