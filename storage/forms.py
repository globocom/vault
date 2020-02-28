# -*- coding: utf-8 -*-

""" Forms for storage.browser """

from django import forms
from django.core import validators


class CreateContainerForm(forms.Form):
    """ Simple form for container creation """
    containername = forms.CharField(label='Container Name', max_length=100, required=True,
        validators=[validators.validate_slug],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'invalid': 'Enter a valid name consisting of letters, numbers, underscores or hyphens.'})


class AddACLForm(forms.Form):
    """ Form for ACLs """
    username = forms.CharField(max_length=100)
    read = forms.BooleanField(required=False)
    write = forms.BooleanField(required=False)


class AddCORSForm(forms.Form):
    """ Form for CORS """
    host = forms.CharField(max_length=100)


class PseudoFolderForm(forms.Form):
    """ Upload form """
    foldername = forms.CharField(label='Pseudofolder Name', max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))


class RemoveCacheForm(forms.Form):
    """ Upload form """
    urls = forms.CharField(label='URLs', required=True,
        widget=forms.Textarea({'cols': 100}))
