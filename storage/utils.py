# -*- coding: utf-8 -*-
# pylint:disable=E0611, E1101

""" Standalone webinterface for Openstack Swift. """

import re
import string
import random
import logging
import dateutil.parser

from urllib.parse import urlparse

from django.conf import settings
from django.contrib import messages
from django.utils.translation import gettext

from swiftclient import client


log = logging.getLogger(__name__)


def get_storage_endpoint(request, endpoint_type):
    """
    service_catalog na sessao eh referente a conexao com o project "admin"
    para retornar o endpoint do "project_id" da sessao, usa-se o service_catalog
    do project "admin", substituindo o project_id

    Isto eh necessario pois a conexao com o Keystone eh sempre com o mesmo
    project, nao estando disponivel de forma direta o service_catalog de um
    project qualquer

    :param request: http resquest
    :param endpoint_type: adminURL, publicURL, internalURL
    :return: endpoint url or None

    """
    service_catalog = request.session.get('service_catalog')
    project_id = request.session.get('project_id')

    if service_catalog is None or project_id is None:
        msg = gettext('No project selected')
        log.error(msg)
        messages.add_message(request, messages.ERROR, msg)
        return None

    service = service_catalog.get('object_store')
    endpoint_on_session = service.get(endpoint_type)

    if endpoint_on_session is None:
        return None

    _, project_admin_id = endpoint_on_session.split('AUTH_')

    final_url = endpoint_on_session.replace(project_admin_id, project_id)

    return final_url


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
            # verifico se e um internal folder
            # se for, preciso redirecionar pra i.s3
            pattern = re.compile('^internal_.+')
            if pattern.match(public_url.split('/')[-1]):
                public_url = public_url.replace('://s3.', '://i.s3.')
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


def get_cors(storage_url, auth_token, container, http_conn):
    """ Returns CORS header of given container. """
    headers = client.head_container(storage_url,
                                    auth_token,
                                    container,
                                    http_conn=http_conn)

    cors = headers.get('x-container-meta-access-control-allow-origin', '')

    return cors


def remove_duplicates(text, separator):
    """ Removes possible duplicates from a separator-separated list. """
    entries = text.split(separator)
    cleaned_entries = list(set(entries))
    text = separator.join(cleaned_entries)
    return text


def remove_duplicates_from_acl(acls):
    """ Removes possible duplicates from a comma-separated list. """
    return remove_duplicates(acls, ',')


def remove_duplicates_from_cors(cors):
    """ Removes possible duplicates from a space-separated list. """
    return remove_duplicates(cors, ' ')


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

    _, objects = client.get_container(storage_url, auth_token, container,
                                      http_conn=http_conn)

    for object in objects:
        object_list.append(object['name'])

    return object_list


def update_swift_account(headers, storage_url, auth_token):
    http_conn = client.http_connection(storage_url, insecure=settings.SWIFT_INSECURE)

    try:
        current_headers = client.head_account(
            storage_url, auth_token, http_conn=http_conn)

        headers.update(current_headers)

        _, body = client.post_account(
            storage_url, auth_token, headers, http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Exception: {}'.format(err))
        return False

    return True


def delete_swift_account(storage_url, auth_token):

    insecure = settings.SWIFT_INSECURE

    try:
        # Criar container vazio para garantir que o account existe no swift
        http_conn = client.http_connection(storage_url, insecure=insecure)

        client.put_container(storage_url, auth_token, 'dummy_container',
                             http_conn=http_conn)
    except client.ClientException as err:
        log.exception('Fail to create container "dummy_container": {0}'.format(err))
        return False

    try:
        # Deletar o account
        url = urlparse(storage_url)
        domain = '{}://{}'.format(url.scheme, url.netloc)
        path = url.path

        http_conn = client.HTTPConnection(domain, insecure=insecure)
        headers = {'X-Auth-Token': auth_token}

        resp = http_conn.request('DELETE', path, headers=headers)

        if resp.status_code != 204:
            log.exception('Fail to delete account {}: status code {}'.format(
                storage_url, resp.status_code
            ))
            return False

    except client.ClientException as err:
        log.exception('Exception: {0}'.format(err))
        return False

    return True


def get_name_from_document(data):
    return data.get('_source').get('object')


def get_uri_object_from_document(data):
    return data.get('hits').get('hits')[0].get('_id')
