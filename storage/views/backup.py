# -*- coding: utf-8 -*-

""" Backup interface views. """

import json
import logging
import requests
import time

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required

from keystoneclient import exceptions

from storage.models import BackupContainer
from storage.utils import get_token_id, get_storage_endpoint
from vault import utils
from identity.keystone import Keystone, exceptions
from actionlogger.actionlogger import ActionLogger


log = logging.getLogger(__name__)
actionlog = ActionLogger()


def _check_backup_user(request, project_id):
    try:
        keystone = Keystone(request)
    except exceptions.AuthorizationFailure:
        msg = _('Unable to retrieve Keystone data')
        messages.add_message(request, messages.ERROR, msg)
        log.error(f'{request.user}: {msg}')

        return False

    if keystone.conn is None:
        log.error('check_backup_user: Keystone connection error')
        return False

    all_users = keystone.user_list()
    backup_user = None
    for user in all_users:
        if user.username == settings.BACKUP_USER:
            backup_user = user

    if backup_user is None:
        log.error('check_backup_user: Undefined backup user')
        return False

    all_roles = keystone.role_list()
    backup_role = None
    for role in all_roles:
        if role.name == settings.BACKUP_USER_ROLE:
            backup_role = role

    if backup_role is None:
        log.error('check_backup_user: Undefined backup role')
        return False

    items = BackupContainer.objects.filter(project_id=project_id)
    if items.count() == 0:
        keystone.remove_user_role(project=project_id,
                                  role=backup_role,
                                  user=backup_user)
        return True

    try:
        keystone.add_user_role(project=project_id,
                               role=backup_role,
                               user=backup_user)
    except exceptions.Conflict:
        log.info('backup_user already with role'.format(project_id))

    return True


def _enable_backup(container, project_id, project_name):
    create_url = 'http://{}:{}@{}/config/create'.format(
        settings.BACKUP_API_USER,
        settings.BACKUP_API_PASSWORD,
        settings.BACKUP_API_URL
    )

    try:
        req = requests.post(create_url, json={
            'name': '{}_{}'.format(project_name, container),
            'type': 'swift',
            'parameters': {
                'endpoint_type': 'admin',
                'env_auth': 'true',
                'tenant': project_name
            }
        })
    except Exception as err:
        log.error('Enable backup error: {}'.format(err))
        return False

    items = BackupContainer.objects.filter(container=container,
                                           project_id=project_id)
    if items.count() > 0:
        return True

    try:
        item = BackupContainer(container=container,
                               project_id=project_id,
                               project_name=project_name)
        item.save()
    except Exception as err:
        log.error('Enable backup error: {}'.format(err))
        return False

    return True


def _disable_backup(container, project_id, project_name):
    delete_url = 'http://{}:{}@{}/config/delete'.format(
        settings.BACKUP_API_USER,
        settings.BACKUP_API_PASSWORD,
        settings.BACKUP_API_URL
    )
    try:
        req = requests.post(delete_url, json={
            'name': '{}_{}'.format(project_name, container)
        })
    except Exception as err:
        log.error('Disable backup error: {}'.format(err))
        return False

    items = BackupContainer.objects.filter(container=container,
                                           project_id=project_id)
    if items.count() == 0:
        return True

    try:
        items[0].delete()
    except Exception as err:
        log.error('Disable backup error: {}'.format(err))
        return False

    return True


@utils.project_required
@login_required
def backup_restore(request, project):
    container = request.POST.get("container")
    project_name = request.POST.get("project_name")
    backup_type = request.POST.get("backup_type")

    content = {'message': ''}
    status = 200

    restore_url = 'http://{}:{}@{}/sync/copy'.format(
        settings.BACKUP_API_USER,
        settings.BACKUP_API_PASSWORD,
        settings.BACKUP_API_URL
    )

    if backup_type == 'daily':
        s3_bucket = 'swift-backup-daily'
    elif backup_type == 'weekly':
        s3_bucket = 'swift-backup-weekly'
    else:
        s3_bucket = 'swift-backup-monthly'

    name = '{}_{}'.format(project_name, container)
    ts = int(time.time())
    restore_container = '{}_{}_{}'.format(container, backup_type, ts)
    content['message'] = 'Backup restaurado no container: {}'.format(restore_container)

    try:
        req = requests.post(restore_url, json={
            "srcFs": "amazon:/{}/{}/{}".format(s3_bucket, project_name, container),
            "dstFs": "{}:/{}".format(name, restore_container),
            "_async": True
        })
        result = req.json()
        content['job'] = result['jobid']
    except Exception as err:
        log.error('Restore backup error: {}'.format(err))
        content['message'] = 'Restore backup error: {}'.format(err)
        return HttpResponse(json.dumps(content),
                            content_type='application/json',
                            status=500)

    return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=200)


def check_backup_conditions(request, container):
    backup_object_count_value = int(settings.BACKUP_OBJECT_COUNT_VALUE)
    backup_object_bytes_value = int(settings.BACKUP_OBJECT_BYTES_VALUE)
    storage_url = get_storage_endpoint(request, 'adminURL')
    headers = {'X-Storage-Token': get_token_id(request)}

    url = '{0}/{1}'.format(storage_url, container)

    response = requests.head(url, headers=headers,
                             verify=not settings.SWIFT_INSECURE)

    if int(response.headers['X-Container-Object-Count']) >= backup_object_count_value:
        return False, _('Error when activating container backup. Container cannot contain more than {} objects').format(backup_object_count_value)

    if int(response.headers['X-Container-Bytes-Used']) >= backup_object_bytes_value:
        return False, _('Error when activating container backup. Container cannot contain more than {}').format(backup_object_count_value)

    return True, 'Success'


@utils.project_required
@login_required
def config_backup_container(request, project, container):
    action = request.GET.get('status')
    if action is None and action not in ['enabled', 'disabled']:
        return HttpResponse(
            json.dumps({'message': _('Wrong "status" parameter')}),
            content_type='application/json',
            status=400
        )

    project_id = request.session.get('project_id')
    project_name = request.session.get('project_name')

    status = 200
    content = {'message': ''}
    result = False
    conditions, msg = check_backup_conditions(request, container)

    if conditions:
        if action == 'enabled':
            result = _enable_backup(container, project_id, project_name)
            msg = '{} "{}"'.format(_('Backup enabled for container'), container)

        if action == 'disabled':
            result = _disable_backup(container, project_id, project_name)
            msg = '{} "{}"'.format(_('Backup disabled for container'), container)

        if result:
            check_ok = _check_backup_user(request, project_id)
            if not check_ok:
                _disable_backup(container, project_id, project_name)
                status = 500
                msg = _("Backup status error: can't set backup user permission")
                log.error('{}. Project: {}, Container: {}'.format(msg,
                                                                  project_name,
                                                                  container))
        else:
            status = 500
            msg = _('Error when updating container backup status')
            log.error('{}. Project: {}, Container: {}'.format(msg,
                                                              project_name,
                                                              container))
    else:
        status = 412

    content['message'] = msg

    return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)


def get_current_backup(container, project_id):
    if not settings.BACKUP_ENABLED:
        return None

    query = BackupContainer.objects.filter(container=container,
                                           project_id=project_id)
    if query.count() > 0:
        return query[0]

    return None


@utils.project_required
@login_required
def container_backup_status(request, project, container):
    project_id = request.session.get('project_id')
    status, content = 200, {'status': 'disabled'}

    if get_current_backup(container, project_id):
        content['status'] = 'enabled'

    return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)


# storage API
def container_backup_list(request):
    status, content = 200, []
    items = BackupContainer.objects.all()

    if items.count() > 0:
        content = [{"container": i.container,
                    "project_id": i.project_id,
                    "project_name": i.project_name} for i in items]
    else:
        status = 404
        log.info(_("Can't find any container to backup"))

    return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)
