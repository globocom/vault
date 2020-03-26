# -*- coding: utf-8 -*-

import logging
from django import forms
from django.forms.widgets import Select
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from keystoneclient import exceptions

from vault.models import GroupProjects
from identity.keystone import KeystoneNoRequest


log = logging.getLogger(__name__)


class VaultLoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(VaultLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class GroupAdminForm(forms.ModelForm):

    class Meta:
        model = Group
        exclude = []

    choices = ((0, ''),)

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save_m2m(self):
        self.instance.user_set.set(self.cleaned_data['users'])

    def save(self, *args, **kwargs):
        instance = super(GroupAdminForm, self).save()
        return instance


def get_project_choices():
    try:
        keystone = KeystoneNoRequest()
    except exceptions.AuthorizationFailure:
        msg = _('Unable to retrieve Keystone data')
        # messages.add_message(request, messages.ERROR, msg)
        log.error(f'In get_project_choices(): {msg}')

        return tuple([(u'', u'---------')])

    project_list = []

    if keystone.conn is not None:
        for project in keystone.project_list():
            project_list.append((project.id, project.name))

    project_list.sort(key=lambda x: x[1].lower())
    project_list = [(u'', u'---------')] + project_list

    return tuple(project_list)


class GroupProjectsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GroupProjectsForm, self).__init__(*args, **kwargs)
        self.fields['project'] = forms.ChoiceField(choices=get_project_choices(), required=True)

    class Meta:
        model = GroupProjects
        fields = ['group', 'project']
