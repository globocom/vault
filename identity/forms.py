# -*- coding:utf-8 -*-

from django import forms
from django.core.validators import RegexValidator
from django.forms.fields import ChoiceField
from django.core import validators

from vault.models import Area

BOOLEAN_CHOICES = ((True, 'Yes'), (False, 'No'))


class UserForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput(), required=False)

    name = forms.CharField(label='User Name', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(label='Email', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    password = forms.CharField(label='Password', required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    password_confirm = forms.CharField(label='Confirm Password', required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    project = ChoiceField(label=u'Primary Project', required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))

    enabled = forms.BooleanField(label=u'Enabled', required=False,
        widget=forms.Select(attrs={'class': 'form-control'},
                            choices=BOOLEAN_CHOICES), initial=True)

    def clean_password(self):
        if 'password' in self.data:
            if self.data['password'] != self.data.get('password_confirm', None):
                raise forms.ValidationError('Passwords did not match')

            return self.data['password']


class CreateUserForm(UserForm):

    role = ChoiceField(label=u'Role', required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))


class UpdateUserForm(UserForm):

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

        for field in ('password', 'password_confirm', 'project'):
            self.fields[field].required = False

        self.fields['project'].widget.attrs['disabled'] = True


class ProjectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        user = kwargs.get('initial').get('user')

        self.fields['groups'].queryset = user.groups.all()

    id = forms.CharField(widget=forms.HiddenInput(), required=False)

    name = forms.CharField(label='Project Name', required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),validators=[
        RegexValidator('^[a-zA-Z0-9_]*$',
            message='Project Name must be an alphanumeric.'
        ),
    ])

    description = forms.CharField(label='Description', required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    enabled = forms.BooleanField(label=u'Enabled', required=False,
        widget=forms.Select(attrs={'class': 'form-control'},
                            choices=BOOLEAN_CHOICES), initial=True)

    areas = forms.ModelChoiceField(label=u'Area', required=True,
        queryset=Area.objects.all())

    groups = forms.ModelChoiceField(label=u'Time', required=True, queryset=None)

    def clean_description(self):
        if 'description' in self.data:
            description = self.data['description']
            if len(description.strip()) == 0:
                raise forms.ValidationError('Project description cannot be empty.')

            return self.data['description']
