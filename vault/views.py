# -*- coding: utf-8 -*-

"""
Vault Generic Views
"""

import json
import logging

from backstage_accounts.views import OAuthBackstageCallback,\
                                     OAuthBackstageRedirect

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponse, HttpResponseRedirect

from keystoneclient.openstack.common.apiclient import exceptions as \
    keystone_exceptions

from actionlogger import ActionLogger

from identity.keystone import Keystone
from vault.utils import update_default_context
from vault.models import Project


log = logging.getLogger(__name__)
actionlog = ActionLogger()


def switch(request, project_id):
    """
    Switch session parameters to project with project_id
    """
    if project_id is None:
        raise ValueError("Missing 'project_id'")

    referer_url = request.META.get('HTTP_REFERER')
    next_url = request.GET.get('next')

    if next_url is None:
        next_url = referer_url

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist as err:
        messages.add_message(request, messages.ERROR, "Can't find this project")
        log.exception('Exception: %s' % err)
        return HttpResponseRedirect(referer_url)

    keystone = Keystone(request)

    request.session['project_id'] = project_id
    request.session['project_name'] = project.name
    request.session['service_catalog'] = keystone.get_endpoints()
    request.session['auth_token'] = keystone.conn.auth_token

    return HttpResponseRedirect(next_url)


class LoginRequiredMixin(object):
    """ Mixin for Class Views that needs a user login """

    def __init__(self):
        self.keystone = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):

        request.session['project_id'] = kwargs.get('project_id')

        try:
            self.keystone = Keystone(request)
        except keystone_exceptions.AuthorizationFailure as err:
            log.error(err)
            msg = 'Object storage authentication failed'
            messages.add_message(request, messages.ERROR, msg)

            return redirect('dashboard')

        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginRequiredMixin, self).get_context_data(**kwargs)

        return update_default_context(self.request, context)


class SuperUserMixin(LoginRequiredMixin):
    """ Mixin for Class Views with superuser powers """

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.WARNING,
                                 u"Unauthorized")

            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

        return super(SuperUserMixin, self).dispatch(*args, **kwargs)


class JSONResponseMixin(object):
    """ Mixin for Class Views with json response """

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        return json.dumps(context)


class SetProjectView(LoginRequiredMixin, View):
    """
    Change the project that the logged user is managing.
    """

    def get(self, request, *args, **kwargs):
        request.session['project_id'] = kwargs.get('project_id')

        try:
            http_redirect = switch(request, kwargs.get('project_id'))
        except ValueError as err:
            http_redirect = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            log.exception('Exception: %s' % err)
            messages.add_message(request, messages.ERROR,
                                 'Unable to change your project.')

        return http_redirect


class OAuthVaultCallback(OAuthBackstageCallback):

    def get_error_redirect(self, provider, reason):
        return reverse('dashboard')

    def get_login_redirect(self, provider, user, access, new=False):
        # Dashboard do admin
        return reverse('dashboard')


class OAuthVaultRedirect(OAuthBackstageRedirect):
    pass


class VaultLogout(View):

    def get(self, request):
        auth_logout(request)
        return HttpResponseRedirect(reverse('dashboard'))
