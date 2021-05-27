# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.forms.fields import ChoiceField

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group

from vault.widgets import PasswordInputWithEye
from identity.keystone import Keystone

BOOLEAN_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)
CLOUD_CHOICES = (
    (None, 'No Cloud'),
    ('gcp', 'Google Cloud')
)


class UserForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput(), required=False)
    id = forms.CharField(widget=forms.HiddenInput(), required=False)

    name = forms.CharField(
        label=_('User Name'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(
        label=_('Email'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    password = forms.CharField(
        label=_('Password'),
        required=True,
        widget=PasswordInputWithEye(attrs={'class': 'form-control'},
                                   render_value=True))

    password_confirm = forms.CharField(
        label=_('Confirm Password'),
        required=True,
        widget=PasswordInputWithEye(attrs={'class': 'form-control'},
                                   render_value=True))

    project = ChoiceField(
        label=_('Primary Project'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}))

    enabled = forms.BooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'},
                            choices=BOOLEAN_CHOICES), initial=True)

    def clean_password(self):
        if 'password' in self.data:
            if self.data['password'] != self.data.get('password_confirm'):
                raise forms.ValidationError(_('Passwords did not match'))

            return self.data['password']


class CreateUserForm(UserForm):

    role = ChoiceField(label=u'Role', required=True,
                       widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)

        _password = Keystone.create_password()

        for field in ('password', 'password_confirm'):
            self.fields[field].initial = _password


class UpdateUserForm(UserForm):

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

        for field in ('password', 'password_confirm', 'project'):
            self.fields[field].required = False

        self.fields['project'].widget.attrs['disabled'] = 'True'


class ProjectForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        user = kwargs.get('initial').get('user')

        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['group'].required = True

        action = kwargs.get('initial').get('action')

        if action == 'update':
            self.fields['name'].widget.attrs['readonly'] = 'True'

    id = forms.CharField(widget=forms.HiddenInput(), required=False)

    action = forms.CharField(widget=forms.HiddenInput(), required=False)

    name = forms.CharField(
        label=_('Project Name'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[
            RegexValidator(
                '^[a-zA-Z0-9_-]*$',
                message=_('Project Name must be an alphanumeric.')
            )
        ]
    )

    description = forms.CharField(
        label=_('Description'),
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    enabled = forms.BooleanField(
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control'},
            choices=BOOLEAN_CHOICES),
        initial=True)

    group = forms.ModelChoiceField(
        label=_('Group'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Group.objects.all())

    if settings.SWIFT_CLOUD_ENABLED:
        cloud = forms.ChoiceField(
            label=_('Cloud Provider'),
            required=False,
            choices=CLOUD_CHOICES,
            widget=forms.Select(attrs={'class': 'form-control'}),
            initial=True)

    def clean_description(self):
        if 'description' in self.data:
            description = self.data['description']
            if len(description.strip()) == 0:
                raise forms.ValidationError(
                    _('Project description cannot be empty.'))

            return self.data['description']


class DeleteProjectConfirm(forms.Form):

    user = forms.CharField(
        label=_('User'),
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Confirm project user'),
            }
        )
    )

    password = forms.CharField(
        label=_('Password'),
        required=True,
        widget=PasswordInputWithEye(
            attrs={
                'class': 'form-control',
                'placeholder': _('Confirm password')
            }
        )
    )
