import logging

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from swiftclient import client

from storage.utils import get_storage_endpoint
from vault.utils import update_default_context

log = logging.getLogger(__name__)


@login_required
def accountview(request, project):
    storage_url = get_storage_endpoint(request, 'adminURL')

    if not storage_url:
        return

    auth_token = request.session.get('auth_token')
    http_conn = client.http_connection(
        storage_url, insecure=settings.SWIFT_INSECURE)

    head_acc = {}
    try:
        head_acc = client.head_account(
            storage_url, auth_token, http_conn=http_conn)
    except Exception as err:
        log.exception(f'Exception: {err}')

    context = {
        'cloud': head_acc.get('x-account-meta-cloud'),
        'total_containers': head_acc.get('x-account-container-count'),
        'total_objects': head_acc.get('x-account-object-count'),
        'total_bytes': head_acc.get('x-account-bytes-used'),
        'account_domain_id': head_acc.get('x-account-project-domain-id'),
    }

    return render(request, 'storage/accountview.html',
                  update_default_context(request, context))
