# -*- coding: utf-8 -*-

from django.forms import ModelForm, ChoiceField, ModelMultipleChoiceField
from django.forms.widgets import Select
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import Group, User

from vault.models import GroupProjects, OG, TeamOG
from identity.keystone import KeystoneNoRequest


class GroupAdminForm(ModelForm):

    class Meta:
        model = Group
        exclude = []

    choices = ((0, ''),)

    og = ChoiceField(
        choices=choices,
        label='OG',
        initial='',
        widget=Select(),
        required=False
    )

    users = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('users', False)
    )

    def __init__(self, *args, **kwargs):
        super(GroupAdminForm, self).__init__(*args, **kwargs)
        og = self.fields['og']
        og.choices += tuple(OG.objects.values_list('id', 'name'))
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()
            try:
                current_og = self.instance.teamog_set.all()[0]
                og.initial = current_og.og_id
            except Exception:
                pass

    def save_m2m(self):
        self.instance.user_set = self.cleaned_data['users']
        team_og = TeamOG()
        if int(self.cleaned_data['og']) != 0:
            if self.instance.teamog_set.all().count() > 0:
                team_og = self.instance.teamog_set.all()[0]
            team_og.og = OG.objects.filter(id=self.cleaned_data['og'])[0]
            team_og.group = self.instance
            self.instance.teamog_set.add(team_og, bulk=False)
        else:
            if self.instance.teamog_set.all().count() > 0:
                team_og = self.instance.teamog_set.all()[0]
                u = team_og.delete()

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
