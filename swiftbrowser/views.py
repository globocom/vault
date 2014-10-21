""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
# pylint:disable=E1101
import hmac
import logging
import os
import requests
import time
import urlparse

from actionlogger import ActionLogger

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from hashlib import sha1

from swiftclient import client

from swiftbrowser.forms import CreateContainerForm, PseudoFolderForm, \
    AddACLForm

from swiftbrowser.utils import replace_hyphens, prefix_list, \
    pseudofolder_object_list, get_temp_key, get_admin_url, \
    get_acls, remove_duplicates_from_acl

from vault.utils import update_default_context


log = logging.getLogger(__name__)
actionlog = ActionLogger()


@login_required
def containerview(request):
    """ Returns a list of all containers in current account. """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    try:
        account_stat, containers = client.get_account(storage_url, auth_token,
                                                      http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR,
                             'Unable to list containers')

        account_stat = {}
        containers = {}

    account_stat = replace_hyphens(account_stat)

    context = update_default_context(request, {
        'account_stat': account_stat,
        'containers': containers,
    })

    return render_to_response('containerview.html', context,
                              context_instance=RequestContext(request))


@login_required
def create_container(request):
    """ Creates a container (empty object of type application/directory) """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
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

    context = update_default_context(request, {
        'form': form,
    })

    return render_to_response('create_container.html', context,
                              context_instance=RequestContext(request))


@login_required
def delete_container(request, container):
    """ Deletes a container """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    try:
        _m, objects = client.get_container(storage_url,
                                           auth_token,
                                           container,
                                           http_conn=http_conn)
        for obj in objects:
            client.delete_object(storage_url, auth_token,
                                 container, obj['name'],
                                 http_conn=http_conn)

        client.delete_container(storage_url, auth_token,
                                container, http_conn=http_conn)
        messages.add_message(request, messages.SUCCESS, "Container deleted.")
        actionlog.log(request.user.username, "delete", container)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')

    return redirect(containerview)


@login_required
def objectview(request, container, prefix=None):
    """ Returns list of all objects in current container. """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    try:
        meta, objects = client.get_container(storage_url, auth_token,
                                             container, delimiter='/',
                                             prefix=prefix,
                                             http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')
        return redirect(containerview)

    prefixes = prefix_list(prefix)
    pseudofolders, objs = pseudofolder_object_list(objects, prefix)

    context = update_default_context(request, {
        'container': container,
        'objects': objs,
        'folders': pseudofolders,
        'prefix': prefix,
        'prefixes': prefixes,
    })

    return render_to_response("objectview.html", context,
                              context_instance=RequestContext(request))


@login_required
def upload(request, container, prefix=None):
    """ Display upload form using swift formpost """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    redirect_url = get_admin_url(request)
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

    context = update_default_context(request, {
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

        storage_url = get_admin_url(request)
        auth_token = request.user.token.id

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

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id

    headers = {
        'X-Storage-Token': auth_token
    }

    url = '{0}/{1}/{2}'.format(storage_url, container, objectname)

    res = requests.get(url, headers=headers, verify=not settings.SWIFT_INSECURE)

    return HttpResponse(res.content, content_type=res.headers['content-type'])


@login_required
def delete_object(request, container, objectname):
    """ Deletes an object """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    try:
        client.delete_object(storage_url, token=auth_token,
                                 container=container, name=objectname,
                                 http_conn=http_conn)
        messages.add_message(request, messages.SUCCESS, 'Object deleted.')
        actionlog.log(request.user.username, "delete", objectname)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        messages.add_message(request, messages.ERROR, 'Access denied.')

    prefix = '/'.join(objectname.split('/')[:-1])

    if prefix:
        prefix += '/'

    if prefix:
        return redirect(objectview, container=container, prefix=prefix)
    else:
        return redirect(objectview, container=container)


@login_required
def delete_pseudofolder(request, container, pseudofolder):
    """ Deletes an empty object, used as a pseudofolder """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
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

    if prefix:
        return redirect(objectview, container=container, prefix=prefix)
    else:
        return redirect(objectview, container=container)


@login_required
def create_pseudofolder(request, container, prefix=None):
    """ Creates a pseudofolder (empty object of type application/directory) """

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
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
            return redirect(objectview, container=container, prefix=prefix)

        return redirect(objectview, container=container)

    prefixes = prefix_list(prefix)

    context = update_default_context(request, {
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

    storage_url = get_admin_url(request)
    auth_token = request.user.token.id
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

    context = update_default_context(request, {
        'container': container,
        'session': request.session,
        'acls': acls,
        'public': public
    })

    return render_to_response('edit_acl.html', context,
                            context_instance=RequestContext(request))
