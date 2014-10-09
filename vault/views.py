# -*- coding:utf-8 -*-

"""
Vault Generic Views
"""

import json
import logging

from openstack_auth.views import switch

from django.conf import settings
from django.contrib import messages
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from actionlogger import ActionLogger
from identity.keystone import Keystone
from vault.utils import update_default_context

log = logging.getLogger(__name__)
actionlog = ActionLogger()


class LoginRequiredMixin(object):
    """ Mixin for Class Views that needs a user login """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
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
        """
        Set project_id on session and switch the user auth to this project
        """
        request.session['project_id'] = kwargs.get('project_id')

        try:
            http_redirect = switch(request, kwargs.get('project_id'))
            messages.add_message(request, messages.INFO,
                                 'Project changed.')
        except ValueError as err:
            http_redirect = HttpResponseRedirect(
                                        request.META.get('HTTP_REFERER'))
            log.exception('Exception: %s' % err)
            messages.add_message(request, messages.ERROR,
                                 'Unable to change your project.')

        return http_redirect
