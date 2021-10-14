# -*- coding: utf-8 -*-

import os
import logging

from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from swiftclient import client

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from keystoneclient import exceptions

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


def generic_pagination(items,
                       page=1,
                       per_page=settings.PAGINATION_SIZE,
                       query=None):
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


def set_current_project(request, project):
    """Set current project on django session"""

    if project is not None:
        request.session['project_id'] = project.id
        request.session['project_name'] = project.name
    else:
        # Project doesn't exist
        request.session.pop('project_id', None)
        request.session.pop('project_name', None)

    return maybe_update_token(request)


def maybe_update_token(request):
    token_time = request.session.get('token_time')

    if token_time is None or token_time < datetime.utcnow():
        log.info('Updating token for user [{}]'.format(request.user))

        try:
            keystone = Keystone(request)
        except exceptions.AuthorizationFailure:
            msg = _('Unable to retrieve Keystone data')
            messages.add_message(request, messages.ERROR, msg)
            log.error(f'{request.user}: {msg}')

            return False

        if keystone.conn is None:
            return False

        request.session['token_time'] = (timedelta(minutes=15) + datetime.utcnow())
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


def project_check(request, current_project):
    project_id = request.session.get('project_id')
    user = request.user

    if current_project:
        try:
            keystone = Keystone(request)
        except exceptions.AuthorizationFailure:
            msg = _('Unable to retrieve Keystone data')
            messages.add_message(request, messages.ERROR, msg)
            log.error(f'{request.user}: {msg}')

            return False

        if not keystone.conn:
            return False

        project = keystone.project_get_by_name(current_project)

        if not project:
            # messages.add_message(request, messages.WARNING, u"Unauthorized")
            return False

        if not project_id or project.id != project_id:
            groups = user.groups.all()
            group_projects = GroupProjects.objects.filter(
                group_id__in=[group.id for group in groups])

            if group_projects.filter(project=project.id).count() == 0:
                # messages.add_message(request, messages.WARNING, u"Unauthorized")
                return False

            save_current_project(user.id, project.id)
            set_current_project(request, project)

    return True


def project_error(request, *args, **kwargs):
    context = {
        "project_name": request.session.get('project_name'),
        "inexistent_project": kwargs.get("inexistent_project"),
        "not_owned_project": kwargs.get("not_owned_project")
    }

    return render(request, "vault/project_error.html", context)


def project_required(view_func):
    def _wrapper(request, *args, **kwargs):
        current_project = kwargs.get('project')

        check = project_check(request, current_project)
        if not check:
            return project_error(request, inexistent_project=kwargs['project'])

        maybe_update_token(request)

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


def encrypt_password(password):
    key = bytes(settings.IDENTITY_SECRET_KEY, encoding='utf8')
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(bytes(password, encoding='utf8'))


def decrypt_password(password):
    key = bytes(settings.IDENTITY_SECRET_KEY, encoding='utf8')
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(bytes(password, encoding='utf8'))
