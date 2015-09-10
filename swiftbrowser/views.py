# -*- coding: utf-8 -*-
# pylint:disable=E1101

""" Standalone webinterface for Openstack Swift. """

import hmac
import logging
import os
import requests
import time
import urlparse
import json

from actionlogger import ActionLogger

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from hashlib import sha1

from swiftclient import client

from swiftbrowser.forms import CreateContainerForm, PseudoFolderForm, \
    AddACLForm, AddCORSForm

from swiftbrowser.utils import replace_hyphens, prefix_list, \
    pseudofolder_object_list, get_temp_key, \
    get_acls, remove_duplicates_from_acl, get_endpoint, get_token_id, \
    get_cors, remove_duplicates_from_cors

from vault import utils

log = logging.getLogger(__name__)
actionlog = ActionLogger()


@login_required
def containerview(request):
    """ Returns a list of all containers in current account. """

    if not request.session.get('project_id'):
        messages.add_message(request, messages.ERROR, 'Select a project')
        return HttpResponseRedirect(reverse('dashboard'))

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    page = request.GET.get('page', 1)

    try:
        account_stat, containers = client.get_account(storage_url, auth_token,
                                                      http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR,
                             'Unable to list containers')

        account_stat = {}
        containers = []

    # Does not show containers used to keep object versions
    version_prefix = settings.SWIFT_VERSION_PREFIX
    if version_prefix:
        containers = [obj for obj in containers
                                if not obj['name'].startswith(version_prefix)]

    account_stat = replace_hyphens(account_stat)

    context = utils.update_default_context(request, {
        'account_stat': account_stat,
        'containers': utils.generic_pagination(containers, page),
    })

    return render_to_response('containerview.html', context,
                              context_instance=RequestContext(request))


@login_required
def create_container(request):
    """ Creates a container (empty object of type application/directory) """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    form = CreateContainerForm(request.POST or None)
    if form.is_valid():
        container = form.cleaned_data['containername']
        try:
            client.put_container(storage_url,
                                 auth_token,
                                 container,
                                 http_conn=http_conn)
            messages.add_message(request, messages.SUCCESS,
                                 "Container created.")

            actionlog.log(request.user.username, "create", container)
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR, 'Access denied.')

        return redirect(containerview)

    context = utils.update_default_context(request, {
        'form': form,
    })

    return render_to_response('create_container.html', context,
                              context_instance=RequestContext(request))


def delete_container(request, container, force=True):
    """
    Deletes a container. If force is True, it will deletes all objects first.
    """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    if force:
        try:
            _, objects = client.get_container(storage_url,
                                           auth_token,
                                           container,
                                           http_conn=http_conn)

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
def delete_container_view(request, container):
    """ Deletes a container """

    response = delete_container(request, container)
    if response:
        messages.add_message(request, messages.SUCCESS, "Container deleted.")
    else:
        messages.add_message(request, messages.ERROR, 'Access denied.')

    return redirect(containerview)


@login_required
def objectview(request, container, prefix=None):
    """ Returns list of all objects in current container. """

    storage_url = get_endpoint(request, 'adminURL')
    public_url = get_endpoint(request, 'publicURL') + '/' + container
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    page = request.GET.get('page', 1)

    try:
        _, objects = client.get_container(storage_url, auth_token,
                                             container, delimiter='/',
                                             prefix=prefix,
                                             http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')
        return redirect(containerview)

    prefixes = prefix_list(prefix)
    object_list = pseudofolder_object_list(objects, prefix, public_url)
    context = utils.update_default_context(request, {
        'container': container,
        'objects': utils.generic_pagination(object_list, page),
        'prefix': prefix,
        'prefixes': prefixes,
    })

    return render_to_response("objectview.html", context,
                              context_instance=RequestContext(request))


@login_required
def upload(request, container, prefix=None):
    """ Display upload form using swift formpost """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    redirect_url = get_endpoint(request, 'adminURL')
    redirect_url += reverse('objectview', kwargs={'container': container, })

    swift_url = storage_url + '/' + container + '/'
    if prefix:
        swift_url += prefix
        redirect_url += prefix

    url_parts = urlparse.urlparse(swift_url)
    path = url_parts.path

    max_file_size = 5 * 1024 * 1024 * 1024
    max_file_count = 1
    expires = int(time.time() + 15 * 60)
    key = get_temp_key(storage_url, auth_token, http_conn)

    if not key:
        messages.add_message(request, messages.ERROR, 'Access denied.')
        if prefix:
            return redirect(objectview, container=container, prefix=prefix)
        else:
            return redirect(objectview, container=container)

    hmac_body = '%s\n%s\n%s\n%s\n%s' % (path, redirect_url, max_file_size,
                                        max_file_count, expires)
    signature = hmac.new(key, hmac_body, sha1).hexdigest()

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

    return render_to_response('upload_form.html', context,
                              context_instance=RequestContext(request))


@login_required
def create_object(request, container, prefix=None):
    """ Create object on Swift """

    obj = request.FILES.get('file1')

    if obj:
        content = obj.read()
        content_type = obj.content_type

        storage_url = get_endpoint(request, 'adminURL')
        auth_token = get_token_id(request)

        storage_url += '/' + container + '/'

        if prefix:
            storage_url += prefix

        storage_url += obj.name

        req = requests.put(storage_url,
                            data=content,
                            headers={
                                'X-Storage-Token': auth_token,
                                'content-type': content_type,
                            },
                            verify=not settings.SWIFT_INSECURE)

        if req.status_code == 201:
            messages.add_message(request, messages.SUCCESS, 'Object created.')
            actionlog.log(request.user.username, "create", obj)
        elif req.status_code == 401 or req.status_code == 403:
            messages.add_message(request, messages.ERROR, 'Access denied.')
        else:
            msg = 'Fail to create object ({0}).'.format(req.status_code)
            log.error(msg)
            messages.add_message(request, messages.ERROR, msg)

    if prefix:
        return redirect(objectview, container=container, prefix=prefix)
    else:
        return redirect(objectview, container=container)


def download(request, container, objectname):
    """ Download an object from Swift """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)

    headers = {
        'X-Storage-Token': auth_token
    }

    url = '{0}/{1}/{2}'.format(storage_url, container, objectname)

    res = requests.get(url, headers=headers, verify=not settings.SWIFT_INSECURE)

    actionlog.log(request.user.username, "download", objectname)

    return HttpResponse(res.content, content_type=res.headers['content-type'])


@login_required
def delete_object_view(request, container, objectname):
    """ Deletes an object """

    response = delete_object(request, container, objectname)

    if response:
        messages.add_message(request, messages.SUCCESS, 'Object deleted.')
    else:
        messages.add_message(request, messages.ERROR, 'Access denied.')

    prefix = '/'.join(objectname.split('/')[:-1])

    if prefix:
        prefix += '/'
        return redirect(objectview, container=container, prefix=prefix)
    else:
        return redirect(objectview, container=container)


def delete_object(request, container, objectname):
    """
    Deletes an object from swift.
    """
    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    try:
        client.delete_object(storage_url,
                             token=auth_token,
                             container=container,
                             name=objectname,
                             http_conn=http_conn)

        actionlog.log(request.user.username, "delete", objectname)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        return False

    return True


@login_required
def delete_pseudofolder(request, container, pseudofolder):
    """ Deletes an empty object, used as a pseudofolder """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    objects = client.get_container(storage_url, auth_token,
                                   container, prefix=pseudofolder,
                                   http_conn=http_conn)[1]

    count_deletes = 0
    for obj in objects:
        try:
            client.delete_object(storage_url, token=auth_token,
                                 container=container, name=obj['name'],
                                 http_conn=http_conn)
            count_deletes += 1
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))

    # Empty pseudofolder
    if count_deletes == 1 and count_deletes == len(objects):
        messages.add_message(request, messages.SUCCESS,
                'Pseudofolder deleted.')

    # Non empty pseudofolder
    elif count_deletes > 1 and count_deletes == len(objects):
        messages.add_message(request, messages.SUCCESS,
                'Pseudofolder and {0} objects deleted.'.format(count_deletes - 1))
    elif count_deletes > 0 and count_deletes < len(objects):
        messages.add_message(request, messages.SUCCESS,
                'It was not possible to delete all objects.')
    else:
        messages.add_message(request, messages.ERROR,
                'Fail to delete pseudofolder.')

    if pseudofolder[-1] == '/':  # deleting a pseudofolder, move one level up
        pseudofolder = pseudofolder[:-1]

    prefix = '/'.join(pseudofolder.split('/')[:-1])

    if prefix:
        prefix += '/'

    actionlog.log(request.user.username, "delete", pseudofolder)

    if prefix:
        return redirect(objectview, container=container, prefix=prefix)
    else:
        return redirect(objectview, container=container)


@login_required
def create_pseudofolder(request, container, prefix=None):
    """ Creates a pseudofolder (empty object of type application/directory) """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

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

        try:
            client.put_object(storage_url, auth_token,
                              container, foldername, obj,
                              content_type=content_type,
                              http_conn=http_conn)
            messages.add_message(request, messages.SUCCESS,
                                 'Pseudofolder created.')
        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR, 'Access denied.')

        if prefix:
            actionlog.log(request.user.username, "create", foldername)
            return redirect(objectview, container=container, prefix=prefix)

        actionlog.log(request.user.username, "create", foldername)
        return redirect(objectview, container=container)

    prefixes = prefix_list(prefix)

    context = utils.update_default_context(request, {
        'container': container,
        'prefix': prefix,
        'prefixes': prefixes,
        'form': form,
    })

    return render_to_response('create_pseudofolder.html', context,
                            context_instance=RequestContext(request))


@login_required
def edit_acl(request, container):
    """ Edit ACLs on given container. """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                        insecure=settings.SWIFT_INSECURE)

    if request.method == 'POST':
        form = AddACLForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            (readers, writers) = get_acls(storage_url,
                                        auth_token,
                                        container,
                                        http_conn)

            readers = remove_duplicates_from_acl(readers)
            writers = remove_duplicates_from_acl(writers)

            if form.cleaned_data['read']:
                readers += ",%s" % username

            if form.cleaned_data['write']:
                writers += ",%s" % username

            headers = {'X-Container-Read': readers,
                       'X-Container-Write': writers}
            try:
                client.post_container(storage_url,
                    auth_token, container, headers=headers, http_conn=http_conn)

                messages.add_message(request, messages.SUCCESS,
                                    'ACLs updated')

                actionlog.log(request.user.username, "update", 'headers: %s, container: %s' % (headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR,
                                    'ACL update failed')

    if request.method == 'GET':
        delete = request.GET.get('delete', None)
        if delete:
            users = delete.split(',')

            (readers, writers) = get_acls(storage_url,
                                            auth_token,
                                            container,
                                            http_conn)

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
                                    'ACL removed.')

                actionlog.log(request.user.username, "delete", 'headers: %s, container: %s' % (headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR,
                                    'ACL update failed.')

    (readers, writers) = get_acls(storage_url, auth_token, container, http_conn)

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

    return render_to_response('edit_acl.html', context,
                              context_instance=RequestContext(request))


@login_required
def metadataview(request, container, objectname=None):
    """ Return object/container/pseudofolder metadata. """

    storage_url = get_endpoint(request, 'adminURL')
    headers = {'X-Storage-Token': get_token_id(request)}

    url = '{0}/{1}'.format(storage_url, container)
    if objectname:
        url = '{0}/{1}'.format(url, objectname)

    response = requests.get(url, headers=headers,
                            verify=not settings.SWIFT_INSECURE)

    content = json.dumps(dict(response.headers))

    status = response.status_code
    if status >= 200 and status < 300 or status == 304:
        status = 200
    else:
        status = 404

    return HttpResponse(content,
                        content_type='application/json',
                        status=status)


@login_required
def object_versioning(request, container, prefix=None):
    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    public_url = get_endpoint(request, 'publicURL') + '/' + container
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    objects = []

    page = request.GET.get('page', 1)

    if request.method == 'GET':
        headers = client.head_container(storage_url,
                                auth_token,
                                container,
                                http_conn=http_conn)

        version_location = headers.get('x-versions-location', None)

        if version_location:
            try:
                _, objects = client.get_container(storage_url,
                                                  auth_token,
                                                  version_location,
                                                  prefix=prefix,
                                                  delimiter='/',
                                                  http_conn=http_conn)
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

        return render_to_response('container_versioning.html',
                                  dictionary=context,
                                  context_instance=RequestContext(request))

    if request.method == 'POST':

        action = request.POST.get('action', None)

        if action == 'enable':
            enable_versioning(request, container)
            actionlog.log(request.user.username, "enable", 'Versioning. Container: %s' % container)
        elif action == 'disable':
            disable_versioning(request, container)
            actionlog.log(request.user.username, "disable", 'Versioning. Container: %s' % container)
        else:
            messages.add_message(request, messages.ERROR, 'Action is required.')

        return redirect(object_versioning, container=container)


def enable_versioning(request, container):
    """ Enable/Disable versioning in container. """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    version_location = '{0}{1}'.format(settings.SWIFT_VERSION_PREFIX, container)

    try:
        client.put_container(storage_url,
                             auth_token,
                             version_location,
                             http_conn=http_conn)

        actionlog.log(request.user.username, "create", version_location)

    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')
        return False

    try:
        header = {'x-versions-location': version_location}
        client.post_container(storage_url,
                                auth_token,
                                container,
                                headers=header,
                                http_conn=http_conn)
        actionlog.log(request.user.username, "update", version_location)

    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')
        return False

    messages.add_message(request, messages.SUCCESS, 'Versioning enabled.')

    return True


def disable_versioning(request, container):
    """ Enable/Disable versioning in container. """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    try:
        headers = client.head_container(storage_url,
                                    auth_token,
                                    container,
                                    http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')
        return False

    version_location = headers.get('x-versions-location', None)

    if version_location:
        try:
            client.post_container(storage_url,
                                  auth_token,
                                  container,
                                  headers={'x-versions-location': ''},
                                  http_conn=http_conn)
            actionlog.log(request.user.username, "update", container)

        except client.ClientException as err:
            log.exception('Exception: {0}'.format(err))
            messages.add_message(request, messages.ERROR, 'Access denied.')
            return False

        deleted = delete_container(request=request, container=version_location)
        if not deleted:
            return False

    messages.add_message(request, messages.SUCCESS, 'Versioning disabled.')

    return True


@login_required
def edit_cors(request, container):
    """ Edit CORS on given container. """

    storage_url = get_endpoint(request, 'adminURL')
    auth_token = get_token_id(request)
    http_conn = client.http_connection(storage_url,
                                        insecure=settings.SWIFT_INSECURE)

    if request.method == 'POST':
        form = AddCORSForm(request.POST)
        if form.is_valid():
            cors = get_cors(storage_url,
                            auth_token,
                            container,
                            http_conn)

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

                messages.add_message(request, messages.SUCCESS,
                                    'CORS updated')

                actionlog.log(request.user.username, "update", 'headers: %s, container: %s' % (headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR,
                                    'CORS update failed')

    if request.method == 'GET':
        delete = request.GET.get('delete', None)
        if delete:
            host = delete.split(' ')

            cors = get_cors(storage_url,
                            auth_token,
                            container,
                            http_conn)

            new_cors = ''
            for element in cors.split(' '):
                if element not in host:
                    new_cors += element
                    new_cors += ' '

            headers = {
                'x-container-meta-access-control-allow-origin': new_cors.strip()
            }

            try:
                client.post_container(storage_url, auth_token,
                              container, headers=headers, http_conn=http_conn)

                messages.add_message(request, messages.SUCCESS,
                                    'CORS removed.')

                actionlog.log(request.user.username, "delete", 'headers: %s, container: %s' % (headers, container))

            except client.ClientException as err:
                log.exception('Exception: {0}'.format(err))
                messages.add_message(request, messages.ERROR,
                                    'CORS update failed.')

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

    return render_to_response('edit_cors.html', context,
                              context_instance=RequestContext(request))
