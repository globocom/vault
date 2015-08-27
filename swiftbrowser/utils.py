""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
# pylint:disable=E0611, E1101
import re
import string
import random
import logging

from swiftclient import client

from django.conf import settings

log = logging.getLogger(__name__)


# TODO: Ajustar para ser compliance com v3
def get_admin_url(request):
    final_url = None
    service_catalog = request.session.get('service_catalog')

    if service_catalog:
        for service in service_catalog:
            if service['type'] == 'object-store':
                final_url = service['endpoints'][0]['adminURL']

    final_url = re.sub(r"\/AUTH_[\w]+\/?$",
                      "/AUTH_%s" % request.session.get('project_id'),
                      final_url)

    return str(final_url)


def get_public_url(request):
    """ Retrieve public URL """

    final_url = None
    service_catalog = request.session.get('service_catalog')

    if service_catalog:
        for service in service_catalog:
            if service['type'] == 'object-store':
                final_url = service['endpoints'][0]['publicURL']

    final_url = re.sub(r"\/AUTH_[\w]+\/?$",
                      "/AUTH_%s" % request.session.get('project_id'),
                      final_url)

    return str(final_url)


def get_token_id(request):
    return request.session.get('auth_token')


def replace_hyphens(olddict):
    """ Replaces all hyphens in dict keys with an underscore.

    Needed in Django templates to get a value from a dict by key name. """
    newdict = {}
    for key, value in olddict.items():
        key = key.replace('-', '_')
        newdict[key] = value
    return newdict


def prefix_list(prefix):
    prefixes = []

    if prefix:
        elements = prefix.split('/')
        elements = filter(None, elements)
        prefix = ""
        for element in elements:
            prefix += element + '/'
            prefixes.append({'display_name': element, 'full_name': prefix})

    return prefixes


def pseudofolder_object_list(objects, prefix, public_url):
    pseudofolders = []
    objs = []
    duplist = []

    for obj in objects:
        # Rackspace Cloudfiles uses application/directory
        # Cyberduck uses application/x-directory
        if obj.get('content_type', None) in ('application/directory',
                                             'application/x-directory'):
            obj['subdir'] = obj['name']

        if 'subdir' in obj:
            # make sure that there is a single slash at the end
            # Cyberduck appends a slash to the name of a pseudofolder
            entry = obj['subdir'].strip('/') + '/'
            if entry != prefix and entry not in duplist:
                duplist.append(entry)
                # pseudofolders.append((entry, obj['subdir']))
                pseudofolders.append({'prefix': entry, 'name': obj['subdir']})
        else:
            obj['public_url'] = public_url + '/' + obj['name']
            objs.append(obj)

    # return (pseudofolders, objs)
    return pseudofolders + objs


def get_temp_key(storage_url, auth_token, http_conn):
    """ Tries to get meta-temp-url key from account.
    If not set, generate tempurl and save it to account.
    This requires at least account owner rights. """

    try:
        account = client.get_account(storage_url, auth_token,
                                http_conn=http_conn)
    except client.ClientException:
        return None

    key = account[0].get('x-account-meta-temp-url-key')

    if not key:
        chars = string.ascii_lowercase + string.digits
        key = ''.join(random.choice(chars) for x in range(32))
        headers = {'x-account-meta-temp-url-key': key}

        try:
            client.post_account(storage_url, token=auth_token, headers=headers,
                                http_conn=http_conn)
        except client.ClientException:
            return None
    return key


def get_acls(storage_url, auth_token, container, http_conn):
    """ Returns ACLs of given container. """
    acls = client.head_container(storage_url,
                                auth_token,
                                container,
                                http_conn=http_conn)

    readers = acls.get('x-container-read', '')
    writers = acls.get('x-container-write', '')
    return (readers, writers)


def remove_duplicates_from_acl(acls):
    """ Removes possible duplicates from a comma-separated list. """
    entries = acls.split(',')
    cleaned_entries = list(set(entries))
    acls = ','.join(cleaned_entries)
    return acls

def get_account_containers(storage_url, auth_token):
    """ List all containers in an account"""
    container_list = []
    http_conn = client.http_connection(storage_url,
                                       insecure=settings.SWIFT_INSECURE)

    _, containers = client.get_account(storage_url, auth_token,
                                                      http_conn=http_conn)

    for container in containers:
        container_list.append(container['name'])

    return container_list

def get_container_objects(container, storage_url, auth_token):
    object_list = []
    http_conn = client.http_connection(storage_url, insecure=settings.SWIFT_INSECURE)

    _, objects = client.get_container(storage_url,
                                           auth_token,
                                           container,
                                           http_conn=http_conn)

    for object in objects:
        object_list.append(object['name'])

    return object_list

def delete_container_and_objects(container, storage_url, auth_token, force=False):
    http_conn = client.http_connection(storage_url, insecure=settings.SWIFT_INSECURE)
    objects = get_container_objects(container, storage_url, auth_token)

    for obj in objects:
        client.delete_object(storage_url,
                      token=auth_token,
                      container=container,
                      name=obj,
                      http_conn=http_conn)

    try:
        client.delete_container(storage_url, auth_token,
                                container, http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        return False

    return True

def delete_swift_account(storage_url, auth_token):
    """"""
    containers = get_account_containers(storage_url, auth_token)

    try:
        for container in containers:
            delete_container_and_objects(container, storage_url, auth_token, force=True)

    #http_conn = client.HTTPConnection(storage_url, insecure=settings.SWIFT_INSECURE)
    #
    #try:
    #   http_conn.request('DELETE', storage_url)
    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        return False

    return True