# -*- coding:utf-8 -*-

from django.conf import settings


def update_default_context(request, context={}):

    context['logged_user'] = request.user
    context['logout_url'] = settings.LOGOUT_URL

    if not request.session.get('project_id'):
        request.session['project_id'] = request.user.project_id

    context['project_id'] = request.session.get('project_id')

    if not request.session.get('has_identity'):
        request.session['has_identity'] = request.user.is_superuser

    context['has_identity'] = request.session.get('has_identity')

    return context
