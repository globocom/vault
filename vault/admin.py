# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from vault.models import GroupProjects
from vault.forms import GroupAdminForm, GroupProjectsForm
from identity.keystone import KeystoneNoRequest


def get_project_list():
    project_list = {}
    try:
        keystone = KeystoneNoRequest()
        if keystone.conn is not None:
            for project in keystone.project_list():
                project_list[project.id] = project.name
    except Exception as e:
        pass

    return project_list


class GroupProjectsAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        self.project_list = get_project_list()
        super(GroupProjectsAdmin, self).__init__(*args, **kwargs)

    form = GroupProjectsForm

    list_display = ('group_name', 'project_name')

    def group_name(self, obj):
        return obj.group.name
    group_name.allow_tags = True
    group_name.short_description = 'group'

    def project_name(self, obj):
        return self.project_list.get(obj.project, '')
    project_name.allow_tags = True
    project_name.short_description = 'project'


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ['permissions']
    search_fields = ['name']


admin.site.register(GroupProjects, GroupProjectsAdmin)
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
admin.site.site_header = "Vault Admin"
