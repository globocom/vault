# -*- coding: utf-8 -*-

from django.forms import ModelForm, ChoiceField, ModelMultipleChoiceField
from django.forms.widgets import Select
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group, User

from vault.models import GroupProjects
from identity.keystone import KeystoneNoRequest


class GroupAdminForm(ModelForm):

    class Meta:
        model = Group
        exclude = []

    choices = ((0, ''),)

    users = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set = self.cleaned_data['users']

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        return instance


def get_project_choices():
    keystone = KeystoneNoRequest()
    project_list = []

    if keystone.conn is not None:
        for project in keystone.project_list():
            project_list.append((project.id, project.name))

    project_list.sort(key=lambda x: x[1].lower())
    project_list = [(u'', u'---------')] + project_list

    return tuple(project_list)


class GroupProjectsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(GroupProjectsForm, self).__init__(*args, **kwargs)
        self.fields['project'] = ChoiceField(choices=get_project_choices(), required=True)

    class Meta:
        model = GroupProjects
        fields = ['group', 'project']
