# -*- coding: utf-8 -*-

import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from keystoneclient import exceptions

from vault.models import GroupProjects
from vault.forms import GroupAdminForm, GroupProjectsForm
from identity.keystone import KeystoneNoRequest


log = logging.getLogger(__name__)


def get_project_list():
    project_list = {}
    try:
        keystone = KeystoneNoRequest()
        if keystone.conn is not None:
            for project in keystone.project_list():
                project_list[project.id] = project.name
    except exceptions.AuthorizationFailure:
        msg = _('Unable to retrieve Keystone data')
        # messages.add_message(request, messages.ERROR, msg)
        log.error(f'In get_project_list(): {msg}')
    except Exception as e:
        pass

    return project_list


class GroupProjectsAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        self.project_list = get_project_list()
        super(GroupProjectsAdmin, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.project_list = get_project_list()
        super(GroupProjectsAdmin, self).__call__(*args, **kwargs)

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
