# -*- coding: utf-8 -*-

"""
Vault Generic Views
"""

import json
import logging

from django.contrib import messages
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login, logout

from keystoneclient.openstack.common.apiclient import exceptions as \
     keystone_exceptions

from django.shortcuts import render_to_response
from django.template import RequestContext

from actionlogger import ActionLogger

from identity.keystone import Keystone
from vault.utils import update_default_context
from vault.models import Project


log = logging.getLogger(__name__)
actionlog = ActionLogger()


def _build_next_url(request):
    n = request.META.get('HTTP_REFERER')

    if request.GET.get('next') is not None:
        n = request.GET.get('next')

    return n if n is not None else reverse('dashboard')


def switch(request, project_id, next_url=None):
    """
    Switch session parameters to project with project_id
    """
    if project_id is None:
        raise ValueError(_("Missing 'project_id'"))

    if next_url is not None:
        next_url = next_url
    else:
        next_url = _build_next_url(request)

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist as err:
        messages.add_message(request, messages.ERROR, _("Can't find this project"))
        log.exception('{}{}'.format(_('Exception:').encode('UTF-8'), err))
        return HttpResponseRedirect(next_url)

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
            msg = _('Object storage authentication failed')
            messages.add_message(request, messages.ERROR, msg)

            return handler500(request)

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
            log.exception('{}{}'.format(_('Exception:').encode('UTF-8'), err))
            messages.add_message(request, messages.ERROR,
                                 _('Unable to change your project.'))

        return http_redirect


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response


def login_user(request):
    #logout(request)
    username = password = ''

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('dashboard'))

    return render_to_response('login.html', context_instance=RequestContext(request))
