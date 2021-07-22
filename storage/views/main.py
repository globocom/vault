# -*- coding: utf-8 -*-
# pylint:disable=E1101

""" Standalone webinterface for Openstack Swift. """

import os
import time
import json
import hmac
import logging
import requests
import re
import ast

from datetime import datetime

from hashlib import sha1
from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template.defaultfilters import filesizeformat

from swiftclient import client

from storage.forms import *
from storage.utils import *

from vault.jsoninfo import JsonInfo
from vault import utils
from actionlogger.actionlogger import ActionLogger


log = logging.getLogger(__name__)
actionlog = ActionLogger()


def connection(request):
    storage_url = get_storage_endpoint(request, 'adminURL')
    conn = client.http_connection(storage_url,
                                  insecure=settings.SWIFT_INSECURE,
                                  timeout=settings.SWIFT_REQUESTS_TIMEOUT)
    return storage_url, conn


@utils.project_required
@login_required
def containerview(request, project):
    """Returns a list of all containers in current account."""

    if not project:
        return redirect('change_project')

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    try:
        account_stat, containers = client.get_account(
            storage_url, auth_token, full_listing=False, http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR,
                             _('Unable to list containers'))
        account_stat, containers = {}, []

    containers = _hide_containers_with_prefixes(containers)
    account_stat = replace_hyphens(account_stat)
    page = request.GET.get('page', 1)

    context = utils.update_default_context(request, {
        'account_stat': account_stat,
        'containers': utils.generic_pagination(containers, page),
    })

    return render(request, 'containerview.html', context)


def _hide_containers_with_prefixes(containers):
    """Hide containers that starts with prefixes listed in SWIFT_HIDE_PREFIXES."""

    hide_prefixes = settings.SWIFT_HIDE_PREFIXES
    if hide_prefixes:
        for prefix in hide_prefixes:
            containers = [
                obj for obj in containers if not obj['name'].startswith(prefix)]

    return containers


@utils.project_required
@login_required
def create_container(request, project):
    """Creates a container (empty object of type application/directory)."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    form = CreateContainerForm(request.POST or None)
    if form.is_valid():
        container = form.cleaned_data['containername']
        project_name = request.session.get('project_name')

        try:
            client.put_container(
                storage_url, auth_token, container, http_conn=http_conn)
            messages.add_message(request, messages.SUCCESS,
                                 _("Container created"))

            actionlog.log(request.user.username, "create", container)
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR, _('Access denied'))

        return redirect(containerview, project=project_name)

    context = utils.update_default_context(request, {
        'form': form,
    })

    return render(request, 'create_container.html', context)


def delete_container(request, container, force=True):
    """Deletes a container. If force is True, it will deletes all objects first."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    if force:
        try:
            meta, objects = client.get_container(
                storage_url, auth_token, container, http_conn=http_conn)
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            return False

        for obj in objects:
            delete_object(request=request,
                          container=container,
                          objectname=obj['name'])
    try:
        client.delete_container(storage_url, auth_token,
                                container, http_conn=http_conn)
        actionlog.log(request.user.username, "delete", container)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        return False

    return True


@login_required
def delete_container_view(request, project, container):
    """Deletes a container."""

    if request.method != 'DELETE':
        return HttpResponse(json.dumps({'message': _('Bad parameters')}),
                            content_type='application/json',
                            status=400)

    status, content = 200, {'message': str(_('Container deleted'))}

    deleted = delete_container(request, container)
    if not deleted:
        status = 500
        msg = str(_('Container delete error'))
        content['message'] = msg
        log.error('{}. Container: {}'.format(msg, container))

    return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)


@utils.project_required
@login_required
def objectview(request, project, container, prefix=None):
    """Returns list of all objects in current container."""

    for hide_prefix in settings.SWIFT_HIDE_PREFIXES:
        if container.startswith(hide_prefix):
            raise Http404("Container does not exist")

    public_url = get_storage_endpoint(request, 'publicURL') + '/' + container
    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    page = request.GET.get('page', 1)

    try:
        meta, objects = client.get_container(storage_url, auth_token,
                                             container, delimiter='/',
                                             prefix=prefix, full_listing=False,
                                             http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, _('Access denied'))
        project_name = request.session.get('project_name')
        return redirect(containerview, project=project_name)

    prefixes = prefix_list(prefix)
    object_list = pseudofolder_object_list(objects, prefix, public_url)

    context = utils.update_default_context(request, {
        'container_meta': meta,
        'container': container,
        'objects': utils.generic_pagination(object_list, page),
        'prefix': prefix,
        'prefixes': prefixes,
    })

    return render(request, "objectview.html", context)


@utils.project_required
@login_required
def object(request, project, container, objectname):
    """Returns selected object in current container."""

    storage_url = get_storage_endpoint(request, 'adminURL')
    headers = {'X-Storage-Token': get_token_id(request)}
    custom_headers = {}
    system_headers = {}

    url = '{0}/{1}'.format(storage_url, container)
    if objectname:
        url = '{0}/{1}'.format(url, str(objectname))

    response = requests.head(url, headers=headers,
                             verify=not settings.SWIFT_INSECURE)

    metadata = dict(response.headers)

    if 'Cache-Control' not in metadata.keys():
        metadata["Cache-Control"] = ''

    public_url = '{}/{}/{}'.format(get_storage_endpoint(request,
                                   'publicURL'), container, objectname)
    prefixes = prefix_list(objectname)

    for item in metadata:
        if 'x-object-meta-' in item.lower():
            custom_headers[re.sub('x-object-meta-', '',
                                  item.lower())] = metadata[item]
        else:
            system_headers[item] = metadata[item]

    context = utils.update_default_context(request, {
        'project': project,
        'container': container,
        'objectname': objectname,
        'public_url': public_url,
        'custom_headers': custom_headers,
        'system_headers': system_headers,
        'prefix': objectname,
        'prefixes': prefixes,
    })

    return render(request, "object.html", context)


@login_required
def upload(request, project, container, prefix=None):
    """Display upload form using swift formpost."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    project_name = request.session.get('project_name')
    redirect_url = 'http://{}'.format(request.get_host())
    redirect_url += reverse('objectview',
        kwargs={'container': container, 'project': project_name})

    swift_url = storage_url + '/' + container + '/'
    if prefix:
        swift_url += prefix
        redirect_url += prefix

    url_parts = urlparse(swift_url)
    path = url_parts.path

    max_file_size = 5 * 1024 * 1024 * 1024
    max_file_count = settings.MAX_FILES_UPLOAD
    expires = int(time.time() + 15 * 60)
    key = get_temp_key(storage_url, auth_token, http_conn)

    if not key:
        messages.add_message(request, messages.ERROR, _('Access denied'))
        if prefix:
            return redirect(objectview, container=container, prefix=prefix, project=project_name)
        else:
            return redirect(objectview, container=container, project=project_name)

    hmac_body = '{}\n{}\n{}\n{}\n{}'.format(
        path, redirect_url, max_file_size, max_file_count, expires)
    signature = hmac.new(
        bytes(key, 'utf-8'), bytes(hmac_body, 'utf-8'), sha1).hexdigest()

    prefixes = prefix_list(prefix)

    context = utils.update_default_context(request, {
        'swift_url': swift_url,
        'redirect_url': redirect_url,
        'max_file_size': max_file_size,
        'max_file_count': max_file_count,
        'expires': expires,
        'signature': signature,
        'container': container,
        'prefix': prefix if prefix is not None else '',
        'prefixes': prefixes,
    })

    return render(request, 'upload_form.html', context)


@login_required
def create_object(request, project, container, prefix=None):
    """Create object on Swift."""

    obj = request.FILES.get('file1')
    project_name = request.session.get('project_name')

    if obj:
        content = obj.read()
        content_type = obj.content_type

        storage_url = get_storage_endpoint(request, 'adminURL')
        auth_token = get_token_id(request)

        storage_url += '/' + container + '/'

        if prefix:
            storage_url += prefix

        storage_url += obj.name

        req = requests.put(storage_url, data=content,
            headers={'X-Storage-Token': auth_token, 'content-type': content_type},
            verify=not settings.SWIFT_INSECURE)

        if req.status_code == 201:
            messages.add_message(
                request, messages.SUCCESS, _('Object created'))
            actionlog.log(request.user.username, "create", obj)
        elif req.status_code == 401 or req.status_code == 403:
            messages.add_message(request, messages.ERROR, _('Access denied'))
        else:
            msg = 'Fail to create object ({0}).'.format(req.status_code)
            log.error(msg)
            messages.add_message(request, messages.ERROR, msg)

    if prefix:
        return redirect(objectview, container=container, prefix=prefix, project=project_name)
    else:
        return redirect(objectview, container=container, project=project_name)


def download(request, project, container, objectname):
    """Download an object from Swift."""

    storage_url = get_storage_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)

    headers = {'X-Storage-Token': auth_token}

    url = '{0}/{1}/{2}'.format(storage_url, container, str(objectname))

    res = requests.get(
        url, headers=headers, verify=not settings.SWIFT_INSECURE)

    actionlog.log(request.user.username, "download", str(objectname))

    return HttpResponse(res.content, content_type=res.headers['Content-Type'])


@login_required
def delete_object_view(request, project, container, objectname):
    """Deletes an object."""

    response = delete_object(request, container, objectname)

    if response:
        messages.add_message(request, messages.SUCCESS, _('Object deleted'))
    else:
        messages.add_message(request, messages.ERROR, _('Access denied'))

    prefix = '/'.join(objectname.split('/')[:-1])
    project_name = request.session.get('project_name')

    if prefix:
        prefix += '/'
        return redirect(objectview, container=container, prefix=prefix, project=project_name)
    else:
        return redirect(objectview, container=container, project=project_name)


def delete_object(request, container, objectname):
    """Deletes an object from swift."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    try:
        client.delete_object(storage_url, token=auth_token,
            container=container, name=objectname, http_conn=http_conn)
        actionlog.log(request.user.username, "delete", objectname)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        return False

    return True


@login_required
def delete_pseudofolder(request, project, container, pseudofolder):
    """Deletes an empty object, used as a pseudofolder."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    objects = client.get_container(storage_url, auth_token,
        container, prefix=pseudofolder, http_conn=http_conn)[1]

    count_deletes = 0

    for obj in objects:
        try:
            client.delete_object(storage_url, token=auth_token,
                container=container, name=obj['name'], http_conn=http_conn)
            count_deletes += 1
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))

    # Empty pseudofolder
    if count_deletes == 1 and count_deletes == len(objects):
        messages.add_message(request, messages.SUCCESS, _('Pseudofolder deleted'))

    # Non empty pseudofolder
    elif count_deletes > 1 and count_deletes == len(objects):
        messages.add_message(request, messages.SUCCESS,
                             'Pseudofolder and {0} objects deleted.'.format(count_deletes - 1))
    elif count_deletes > 0 and count_deletes < len(objects):
        messages.add_message(request, messages.SUCCESS,
                             _('Could not delete all objects'))
    else:
        messages.add_message(request, messages.ERROR,
                             _('Fail to delete pseudofolder'))

    if pseudofolder[-1] == '/':  # deleting a pseudofolder, move one level up
        pseudofolder = pseudofolder[:-1]

    prefix = '/'.join(pseudofolder.split('/')[:-1])

    if prefix:
        prefix += '/'

    project_name = request.session.get('project_name')
    actionlog.log(request.user.username, "delete", pseudofolder)

    if prefix:
        return redirect(objectview, container=container, prefix=prefix, project=project_name)
    else:
        return redirect(objectview, container=container, project=project_name)


@login_required
def create_pseudofolder(request, project, container, prefix=None):
    """Creates a pseudofolder (empty object of type application/directory)."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    form = PseudoFolderForm(request.POST or None)

    if form.is_valid():
        foldername = request.POST.get('foldername', None)
        if prefix:
            foldername = prefix + '/' + foldername
        foldername = os.path.normpath(foldername)
        foldername = foldername.strip('/')
        foldername += '/'

        content_type = 'application/directory'
        obj = None
        project_name = request.session.get('project_name')

        try:
            client.put_object(storage_url, auth_token, container,
                foldername, obj, content_type=content_type, http_conn=http_conn)
            messages.add_message(request, messages.SUCCESS,
                                 _('Pseudofolder created'))
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR, _('Access denied'))

        if prefix:
            actionlog.log(request.user.username, "create", foldername)
            return redirect(objectview, container=container, prefix=prefix, project=project_name)

        actionlog.log(request.user.username, "create", foldername)
        return redirect(objectview, container=container, project=project_name)

    prefixes = prefix_list(prefix)

    context = utils.update_default_context(request, {
        'container': container,
        'prefix': prefix,
        'prefixes': prefixes,
        'form': form,
    })

    return render(request, 'create_pseudofolder.html', context)


@login_required
def edit_acl(request, project, container):
    """Edit ACLs on given container."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    if request.method == 'POST':
        form = AddACLForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            readers, writers = get_acls(
                storage_url, auth_token, container, http_conn)

            readers = remove_duplicates_from_acl(readers)
            writers = remove_duplicates_from_acl(writers)

            if form.cleaned_data['read']:
                readers += ",{}".format(username)

            if form.cleaned_data['write']:
                writers += ",{}".format(username)

            headers = {'X-Container-Read': readers,
                       'X-Container-Write': writers}
            try:
                client.post_container(storage_url,
                    auth_token, container, headers=headers, http_conn=http_conn)

                messages.add_message(request, messages.SUCCESS, _('ACLs updated'))

                actionlog.log(request.user.username, "update",
                              'headers: {}, container: {}'.format(headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR,
                                     _('ACL update failed'))

    if request.method == 'GET':
        delete = request.GET.get('delete', None)
        if delete:
            users = delete.split(',')

            (readers, writers) = get_acls(storage_url, auth_token,
                                          container, http_conn)

            new_readers = ''
            for element in readers.split(','):
                if element not in users:
                    new_readers += element
                    new_readers += ","

            new_writers = ''
            for element in writers.split(','):
                if element not in users:
                    new_writers += element
                    new_writers += ","

            headers = {'X-Container-Read': new_readers,
                       'X-Container-Write': new_writers}
            try:
                client.post_container(storage_url, auth_token,
                                      container, headers=headers, http_conn=http_conn)

                messages.add_message(request, messages.SUCCESS,
                                     _('ACL removed'))

                actionlog.log(request.user.username, "delete",
                              'headers: {}, container: {}'.format(headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR,
                                     _('ACL update failed'))

    readers, writers = get_acls(
        storage_url, auth_token, container, http_conn)

    acls = {}

    if readers != '':
        readers = remove_duplicates_from_acl(readers)
        for entry in readers.split(','):
            acls[entry] = {}
            acls[entry]['read'] = True
            acls[entry]['write'] = False

    if writers != '':
        writers = remove_duplicates_from_acl(writers)
        for entry in writers.split(','):
            if entry not in acls:
                acls[entry] = {}
                acls[entry]['read'] = False
            acls[entry]['write'] = True

    public = False
    if acls.get('.r:*', False):
        public = True

    context = utils.update_default_context(request, {
        'container': container,
        'session': request.session,
        'acls': acls,
        'public': public
    })

    return render(request, 'edit_acl.html', context)


@login_required
def make_public(request, container):
    """Enable/Disable public access to a container."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    headers = client.head_container(
        storage_url, auth_token, container, http_conn=http_conn)

    current = headers.get('X-Container-Read')
    if current is None:
        headers['X-Container-Read'] = '.r:*'
        message = _('Container is now public')
    else:
        del headers['X-Container-Read']
        message = _('Container is now private')

    try:
        client.post_container(storage_url,
            auth_token, container, headers=headers, http_conn=http_conn)

        content = {"message": str(message)}
        msg = "X-Container-Read header on container {}".format(container)
        actionlog.log(request.user.username, "update", msg)
    except client.ClientException as err:
        content, status = {"message": str(
            _("Container ACL update failed"))}, 500
        log.exception("Exception: {}".format(err))

    return HttpResponse(
        json.dumps(content), content_type='application/json', status=status)


@login_required
def metadataview(request, project, container, objectname=None):
    """Return object/container/pseudofolder metadata."""

    storage_url = get_storage_endpoint(request, 'adminURL')
    headers = {'X-Storage-Token': get_token_id(request)}

    url = '{0}/{1}'.format(storage_url, container)
    if objectname:
        url = '{0}/{1}'.format(url, str(objectname))

    response = requests.head(
        url, headers=headers, verify=not settings.SWIFT_INSECURE)

    content = json.dumps(dict(response.headers))

    status = response.status_code
    if status >= 200 and status < 300 or status == 304:
        status = 200
    else:
        status = 404

    return HttpResponse(
        content, content_type='application/json', status=status)


@login_required
def object_versioning(request, project, container, prefix=None):
    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)
    public_url = get_storage_endpoint(request, 'publicURL') + '/' + container

    objects = []

    page = request.GET.get('page', 1)

    if request.method == 'GET':
        headers = client.head_container(
            storage_url, auth_token, container, http_conn=http_conn)

        version_location = headers.get('x-versions-location', None)

        if version_location:
            try:
                meta, objects = client.get_container(
                    storage_url, auth_token, version_location, prefix=prefix,
                    delimiter='/', full_listing=False, http_conn=http_conn)
            except client.ClientException:
                pass

        prefixes = prefix_list(prefix)
        object_list = pseudofolder_object_list(objects, prefix, public_url)

        context = utils.update_default_context(request, {
            'container': container,
            'objects': utils.generic_pagination(object_list, page),
            'version_location': version_location,
            'prefix': prefix,
            'prefixes': prefixes,
        })

        return render(request, 'container_versioning.html', context)

    if request.method == 'POST':

        action = request.POST.get('action', None)

        if action == 'enable':
            enable_versioning(request, container)
            actionlog.log(request.user.username, "enable",
                          'Versioning. Container: {}'.format(container))
        elif action == 'disable':
            disable_versioning(request, container)
            actionlog.log(request.user.username, "disable",
                          'Versioning. Container: {}'.format(container))
        else:
            messages.add_message(request, messages.ERROR,
                                 'Action is required.')

        return redirect(object_versioning, project=project, container=container)


def enable_versioning(request, container):
    """Enable/Disable versioning in container."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    version_location = '{0}{1}'.format(
        settings.SWIFT_VERSION_PREFIX, container)

    try:
        client.put_container(
            storage_url, auth_token, version_location, http_conn=http_conn)
        actionlog.log(request.user.username, "create", version_location)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return False

    try:
        header = {'x-versions-location': version_location}
        client.post_container(storage_url,
            auth_token, container, headers=header, http_conn=http_conn)
        actionlog.log(request.user.username, "update", version_location)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return False

    messages.add_message(request, messages.SUCCESS, _('Versioning enabled'))

    return True


def disable_versioning(request, container):
    """Enable/Disable versioning in container."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    try:
        headers = client.head_container(
            storage_url, auth_token, container, http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, _('Access denied'))
        return False

    version_location = headers.get('x-versions-location', None)

    if version_location:
        try:
            client.post_container(storage_url, auth_token, container,
                headers={'x-versions-location': ''}, http_conn=http_conn)
            actionlog.log(request.user.username, "update", container)
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR, _('Access denied'))
            return False

        deleted = delete_container(request=request, container=version_location)
        if not deleted:
            return False

    messages.add_message(request, messages.SUCCESS, _('Versioning disabled'))

    return True


@login_required
def edit_cors(request, project, container):
    """Edit CORS on given container."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    if request.method == 'POST':
        form = AddCORSForm(request.POST)
        if form.is_valid():
            cors = get_cors(
                storage_url, auth_token, container, http_conn)

            cors = remove_duplicates_from_cors(cors)

            host = form.cleaned_data['host']
            if host:
                cors += " {}".format(host)

            headers = {
                'x-container-meta-access-control-allow-origin': cors.strip()
            }

            try:
                client.post_container(storage_url,
                    auth_token, container, headers=headers, http_conn=http_conn)

                messages.add_message(request, messages.SUCCESS, _('CORS updated'))

                actionlog.log(request.user.username, "update",
                              'headers: {}, container: {}'.format(headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR, _('CORS update failed'))

    if request.method == 'GET':
        delete = request.GET.get('delete', None)
        if delete:
            host = delete.split(' ')
            cors = get_cors(storage_url, auth_token, container, http_conn)

            new_cors = ''
            for element in cors.split(' '):
                if element not in host:
                    new_cors += element
                    new_cors += ' '

            headers = {
                'x-container-meta-access-control-allow-origin': new_cors.strip()
            }

            try:
                client.post_container(storage_url,
                    auth_token, container, headers=headers, http_conn=http_conn)

                messages.add_message(request, messages.SUCCESS, _('CORS removed'))

                actionlog.log(request.user.username, "delete",
                              'headers: {}, container: {}'.format(headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR, _('CORS update failed'))

    cors = get_cors(storage_url, auth_token, container, http_conn)

    context = utils.update_default_context(request, {
        'container': container,
        'session': request.session,
        'cors': [],
    })

    if cors != '':
        cors = remove_duplicates_from_cors(cors)
        for entry in cors.split(' '):
            context['cors'].append(entry)

    return render(request, 'edit_cors.html', context)


@utils.project_required
@login_required
def remove_from_cache(request, project):
    form = RemoveCacheForm(request.POST or None)

    if form.is_valid():
        urls = form.cleaned_data['urls'].splitlines()

        data = {
            'url': urls,
            'user': request.user.username
        }

        api_url = '{host}/url/add'.format(host=settings.CACHESWEEP_API)
        req = requests.post(api_url, json=data)

        if req.status_code == 201:
            messages.add_message(request, messages.SUCCESS,
                _('URLs scheduled to be removed. Grab some coffee, it takes 2 to 3 minutes to remove.'))

            form = RemoveCacheForm(None)
            actionlog.log(request.user.username, "remove_cache", repr(urls))
        else:
            messages.add_message(request, messages.ERROR,
                _('Fail to schedule URLs to be removed.'))

    context = utils.update_default_context(request, {'form': form})

    return render(request, 'remove_from_cache.html', context)


@utils.project_required
@login_required
def edit_custom_metadata(request, project, container, objectname):
    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    content, status = {}, 200
    custom_headers = request.POST.dict()
    system_headers = {}

    headers = client.head_object(storage_url,
        auth_token, container, objectname, http_conn=http_conn)

    for item in headers:
        if 'x-object-meta-' not in item.lower():
            system_headers[item] = headers[item]

    system_headers.update(custom_headers)

    try:
        client.post_object(storage_url, auth_token, container,
            objectname, headers=system_headers, http_conn=http_conn)

        content = {"message": _("Custom Metadata updated")}
        msg = "Custom Metadata header on object {}/{}".format(container, objectname)
        actionlog.log(request.user.username, "update", msg)
    except client.ClientException as err:
        content, status = {"message": str(
            _("Custom Metadata update failed"))}, 500
        log.exception("Exception: {}".format(err))

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@login_required
def cache_control(request, project, container, objectname):
    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    content, status = {}, 200
    unit = request.POST.get("unit", "minutes")
    maxage = int(request.POST.get("maxage", 3)) * 60

    if maxage <= 0:
        content, status = {"message": _("Days must be greater than 0")}, 400
        return HttpResponse(
            json.dumps(content), content_type='application/json', status=status)

    if unit == "hours":
        maxage = maxage * 3600
    elif unit == "days":
        maxage = maxage * 86400

    headers = client.head_object(storage_url,
        auth_token, container, objectname, http_conn=http_conn)
    headers["cache-control"] = "public, max-age={}".format(maxage)

    try:
        client.post_object(storage_url, auth_token,
            container, objectname, headers=headers, http_conn=http_conn)
        content = {"message": str(
            _("Cache-Control updated")), "cache_control": headers["cache-control"]}
        msg = "Cache-Control header on object {}/{}".format(container,
                                                            objectname)
        actionlog.log(request.user.username, "update", msg)
    except client.ClientException as err:
        content, status = {"message": str(
            _("Cache-Control update failed"))}, 500
        log.exception("Exception: {}".format(err))

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@login_required
def optional_headers(request, project, container, objectname):
    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    content, status = {}, 200

    headers = client.head_object(storage_url,
        auth_token, container, objectname, http_conn=http_conn)

    body_dict = ast.literal_eval(request.body.decode())
    headers['x-delete-at'] = body_dict.get('x-delete-at')
    log.error(headers['x-delete-at'])
    if (headers['x-delete-at'] == ''):
        headers.pop('x-delete-at', None)

    content = {"message": str(_("Optional headers updated")),
               "x-delete-at": headers.get("x-delete-at")}
    try:
        client.post_object(storage_url, auth_token, container, objectname,
                           headers=headers, http_conn=http_conn)
    except Exception as e:
        log.error(e)
        content, status = {"message": str(
            _("Optional headers update failed: {}".format(e)))}, 500

    return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)


@utils.project_required
@login_required
def get_deleted_objects(request, project, container, prefix=None):
    """Return all deleted objects from a given container."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)
    public_url = get_storage_endpoint(request, 'publicURL')
    trash_container = "{}-{}".format(settings.SWIFT_TRASH_PREFIX, container)
    objects = None

    try:
        meta, objects = client.get_container(storage_url,
            auth_token, trash_container, delimiter='', http_conn=http_conn)
    except client.ClientException as err:
        if err.http_status == 404:
            log.info("Not found: {}".format(trash_container))
            objects = []
        else:
            log.exception("Exception: {0}".format(err.msg))
            status = err.http_status
            content = {"error": err.msg}

    if objects is not None:
        object_list = pseudofolder_object_list(objects, prefix, public_url)

        deleted = []
        for item in object_list:
            if 'prefix' not in item:
                name = item.get('name')
                deleted.append({
                    "name": name,
                    "size": item.get('bytes')
                })

        status = 200
        content = {
            "deleted_objects": deleted,
            "prefix": prefix,
            "storage_url": storage_url,
            "original_container": container,
            "trash_container": trash_container
        }

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@utils.project_required
@login_required
def restore_object(request, project):
    """Restore a object from trash."""

    if request.method != 'POST':
        return HttpResponse(status=405)

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    container = request.POST.get("container")
    trash_container = request.POST.get("trash_container")
    object_name = request.POST.get("object_name")
    object_new_name = request.POST.get("object_new_name")

    content = {}
    status = 200

    # valida se objeto a ser restaurado da lixeira já existe no container.
    try:
        if object_new_name != '':
            client.head_object(storage_url,
                auth_token, container, object_new_name, http_conn=http_conn)
        else:
            client.head_object(storage_url,
                auth_token, container, object_name, http_conn=http_conn)

        status = 409

        # Novo nome será o nome original + timestamp + extensão
        new_object_name = object_name.rsplit('.', 1)
        orignal_name = new_object_name[0] + '_'
        time_stamp = datetime.isoformat(datetime.now())
        extension_object = '.' + new_object_name[1]

        final_new_object_name = orignal_name + time_stamp + extension_object
        content = {
            'original_object_name': object_name,
            'new_object_name': final_new_object_name
        }

    except client.ClientException as err:
        # Segue o fluxo normal se objeto a ser restaurado não foi localizado no container
        obj_headers = client.head_object(storage_url,
            auth_token, trash_container, object_name, http_conn=http_conn)
        custom_headers = {
            "X-Fresh-Metadata": "True",
            "X-Copy-From": "/{}/{}".format(trash_container, object_name)
        }
        for key, value in obj_headers.items():
            if "x-object-meta" in key:
                custom_headers[key] = value

        # Upload do objeto para o container de origem
        try:
            if object_new_name != '':
                client.put_object(storage_url, auth_token, container, object_new_name,
                    content_length=0, headers=custom_headers, http_conn=http_conn)
            else:
                client.put_object(storage_url, auth_token, container, object_name,
                    content_length=0, headers=custom_headers, http_conn=http_conn)
            messages.add_message(request, messages.SUCCESS,
                                 _('Object restored'))
            actionlog.log(request.user.username, "restore", object_name)
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err.msg))
            status = err.http_status
            content = {"error": err.msg}

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@utils.project_required
@login_required
def remove_from_trash(request, project):

    if request.method != 'POST':
        return HttpResponse(status=405)

    trash_container = request.POST.get("trash_container")
    object_name = request.POST.get("object_name")

    result = delete_object(request, trash_container, object_name)

    status = 202
    content = {}

    if not result:
        status = 500
        content = {
            "error": "Object '{}' was not removed from trash".format(object_name)
        }

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@utils.project_required
@login_required
def config_trash_container(request, project, container):
    """Enable or disable container trash with the metadata X-Undelete-Enabled configured to True or False."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    status, content = 200, {'message': ''}
    enable = False
    content['message'] = (
        '{} "{}"'.format(_('Trash disabled for container'), container)
    )

    try:
        if request.GET.get('status').lower() == 'enabled':
            enable = True
            content['message'] = (
                '{} "{}"'.format(_('Trash enabled for container'), container)
            )

        client.put_container(storage_url, auth_token, container,
            headers={'X-Storage-Token': auth_token, 'X-Undelete-Enabled': str(enable)},
            http_conn=http_conn)

        # messages.add_message(request, messages.SUCCESS, msg)
        actionlog.log(request.user.username, 'update_trash', container)
    except Exception as err:
        log.exception('Exception: {0}'.format(err))
        # messages.add_message(request, messages.ERROR, _('Update container trash error'))
        status, content = 500, {'message': 'Update container trash error'}

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@utils.project_required
@login_required
def container_trash_status(request, project, container):
    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    status, content = 200, {'status': 'enabled'}
    try:
        headers = client.head_container(storage_url,
            auth_token, container, http_conn=http_conn)

        undelete_enabled = headers.get('x-undelete-enabled')
        if undelete_enabled is None or undelete_enabled == 'False':
            content['status'] = 'disabled'

    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, _('Access denied'))
        status, content = 500, {'message': 'Access denied'}

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@login_required
def container_acl_update(request, project, container):
    """Sets a container to public or private."""

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    headers = client.head_container(storage_url,
        auth_token, container, http_conn=http_conn)

    msg = ''
    public = False
    if request.GET.get('status').lower() == 'enabled':
        headers['x-container-read'] = '.r:*'
        msg = _('Container is now public')
        public = True
    else:
        headers['x-container-read'] = ''
        msg = str(_('Container is now private'))

    status, content = 200, {'message': str(msg)}

    try:
        client.post_container(storage_url,
            auth_token, container, headers=headers, http_conn=http_conn)
        if public:
            actionlog.log(request.user.username, "set_public", container)
        else:
            actionlog.log(request.user.username, "set_private", container)
    except Exception as err:
        log.exception('Exception: {0}'.format(err))
        status, content = 500, {'message': 'Failed on update container ACL'}

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


@utils.project_required
@login_required
def container_acl_status(request, project, container):
    """
    Makes a head in a container and returns to the context
    status = enabled if it's public, status = disabled for private
    """

    auth_token = get_token_id(request)
    storage_url, http_conn = connection(request)

    status, content = 200, {'status': 'disabled'}
    try:
        headers = client.head_container(storage_url,
            auth_token, container, http_conn=http_conn)

        acl_header = headers.get('x-container-read', '')
        if '.r:*' in acl_header:
            content['status'] = 'enabled'

    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, _('Access denied'))
        status, content = 500, {'message': 'Access denied'}

    return HttpResponse(json.dumps(content),
        content_type='application/json', status=status)


class SwiftJsonInfo(JsonInfo):

    def generate_menu_info(self):
        project_name = self.request.session.get('project_name')
        return {
            "name": str(_("Object Storage")),
            "icon": "fas fa-cube",
            "url": reverse("containerview", kwargs={'project': project_name}),
            "subitems": [
                # {
                #     "name": str(_("Account")),
                #     "icon": "",
                #     "url": reverse("accountview", kwargs={'project': project_name})
                # },
                {
                    "name": str(_("Containers")),
                    "icon": "",
                    "url": reverse("containerview", kwargs={'project': project_name})
                }
            ]
        }

    def generate_widget_info(self):
        storage_url, http_conn = connection(self.request)
        auth_token = self.request.session.get('auth_token')
        project_name = self.request.session.get('project_name')

        if storage_url is None:
            return {"error": "Storage URL not found."}

        try:
            head_acc = client.head_account(
                storage_url, auth_token, http_conn=http_conn)
        except Exception as err:
            log.exception('Exception: {0}'.format(err))
            return {"error": "Unable to show Swift info."}

        widget_info = [{
            "type": "default",
            "name": "storage",
            "title": str(_("Swift")),
            "subtitle": str(_("Object Storage")),
            "color": "red",
            "icon": "fas fa-cube",
            "url": reverse("containerview", kwargs={'project': project_name}),
            "properties": [
                {
                    "name": str(_("containers")),
                    "description": "",
                    "value": head_acc.get('x-account-container-count')
                },
                {
                    "name": str(_("objects")),
                    "description": "",
                    "value": head_acc.get('x-account-object-count')
                },
                {
                    "name": str(_("used space")),
                    "description": "",
                    "value": filesizeformat(head_acc.get('x-account-bytes-used'))
                }
            ],
            "buttons": [
                {
                    "name": str(_("Containers")),
                    "url": reverse("containerview", kwargs={'project': project_name})
                }
            ]
        }]

        if 'x-account-meta-cloud' in head_acc:
            widget_info[0]['extra'] = {
                "icon": "fas fa-cloud",
                "title": str(_("This project saves its objects in a public cloud"))
            }

        return widget_info


@utils.project_required
@login_required
def info_json(request, project=None):
    sjinfo = SwiftJsonInfo(request=request)
    return sjinfo.render(request)
