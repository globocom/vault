# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime, timedelta

from swiftclient import client

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from vault.models import GroupProjects, CurrentProject
from identity.keystone import Keystone, KeystoneNoRequest


log = logging.getLogger(__name__)


def update_default_context(request, context={}):
    if not request.session.get('is_superuser'):
        request.session['is_superuser'] = request.user.is_superuser

    context.update({
        'logged_user': request.user,
        'project_id': request.session.get('project_id'),
        'project_name': request.session.get('project_name'),
        'is_superuser': request.user.is_superuser
    })

    return context


def generic_pagination(items, page=1, per_page=settings.PAGINATION_SIZE, query=None):
    paginator = Paginator(items, per_page)

    try:
        paginated_items = paginator.page(page)
        if (query):
            paginated_items.query = query
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_items = paginator.page(paginator.num_pages)

    return paginated_items


def save_current_project(user_id, project_id):
    """Save on database user current project"""

    try:
        current = CurrentProject.objects.get(user_id=user_id)
    except CurrentProject.DoesNotExist:
        current = CurrentProject()
        current.user_id = user_id

    current.project = project_id
    current.save()

    return current


def set_current_project(request, project_name):
    """Set current project on django session"""

    keystone = KeystoneNoRequest()
    project = keystone.project_get_by_name(project_name)

    request.session['project_id'] = project.id
    request.session['project_name'] = project.name

    return maybe_update_token(request)


def maybe_update_token(request):
    token_time = request.session.get('token_time')

    if token_time is None or token_time < datetime.utcnow():
        log.info('Updating token for user [{}]'.format(request.user))

        keystone = Keystone(request)

        if keystone.conn is None:
            return False

        request.session['token_time'] = (
            timedelta(minutes=15) + datetime.utcnow()
        )
        request.session['auth_token'] = keystone.conn.auth_token
        request.session['service_catalog'] = keystone.get_endpoints()

        return True

    return False


def get_current_project(user_id):
    """Return from database user current project"""

    try:
        current = CurrentProject.objects.get(user_id=user_id)
    except CurrentProject.DoesNotExist:
        return None

    keystone = KeystoneNoRequest()
    return keystone.project_get(current.project)


def delete_current_project(user_id):
    """Delete from database user current project and removes it from session"""

    try:
        current = CurrentProject.objects.get(user_id=user_id)
        current.delete()
    except Exception:
        return False

    request.session.pop('project_id')
    request.session.pop('project_name')

    return True


def purge_current_project(request, project_id):
    """Delete all entries for project_id and removes it from session"""

    try:
        items = CurrentProject.objects.filter(project=project_id)
        items.delete()
    except Exception:
        return False

    request.session.pop('project_id')
    request.session.pop('project_name')

    return True


def project_required(view_func):
    def _wrapper(request, *args, **kwargs):
        project_name = request.session.get('project_name')

        if 'project' in kwargs:
            if project_name != kwargs['project']:
                set_current_project(request, project_name)

        maybe_update_token(request)

        if project_name is None:
            messages.add_message(
                request, messages.ERROR, _('Select a project')
            )
            return HttpResponseRedirect(reverse('dashboard_noproject'))

        return view_func(request, *args, **kwargs)

    return _wrapper


def human_readable(value):
    """
    Returns the number in a human readable format; for example 1048576 = "1Mi".
    """
    value = float(value)
    index = -1
    suffixes = 'KMGTPEZY'
    while value >= 1024 and index + 1 < len(suffixes):
        index += 1
        value = round(value / 1024)
    if index == -1:
        return '{:d}'.format(value)
    return '{:d}{}i'.format(round(value), suffixes[index])
