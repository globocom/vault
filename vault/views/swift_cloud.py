import json
import logging
import pdb
from urllib import response
from swiftclient import client
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from identity.keystone import Keystone
from vault.models import GroupProjects
from swift_cloud_tools.client import SCTClient

log = logging.getLogger(__name__)


def get_conn_and_storage_url(request, project_id):
    service_catalog = request.session.get('service_catalog')
    service = service_catalog.get('object_store')
    endpoint = service.get('adminURL')
    _, current_id = endpoint.split('AUTH_')
    storage_url = endpoint.replace(current_id, project_id)
    http_conn = client.http_connection(storage_url,
        insecure=settings.SWIFT_INSECURE)

    return http_conn, storage_url


@login_required
def swift_cloud_report(request):
    try:
        keystone = Keystone(request)
    except Exception as err:
        log.exception(f"Keystone error: {err}")
        return render(request, "vault/swift_cloud/report.html",
            {"projects": []})

    environ = settings.ENVIRON
    if not environ and "localhost" in request.get_host():
        environ = "local"

    projects = []
    try:
        for project in keystone.project_list():
            projects.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "environment": environ,
                "status": "",
            })
        projects.sort(key=lambda p: p["name"].lower())
    except Exception as err:
        log.exception(f"Keystone error: {err}")

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY
    )

    data = []
    try:
        reponse = sct_client.transfer_status_by_projects(
            [p["id"] for p in projects])
        if reponse and reponse.status_code == 200:
            data = reponse.json()
    except Exception as err:
        log.exception(f"Swift Cloud Tools Error: {err}")

    return render(request, "vault/swift_cloud/report.html",
        {"projects": json.dumps(projects),
         "migration_data": json.dumps(data)})


@login_required
def swift_cloud_status(request):
    try:
        keystone = Keystone(request)
    except Exception as err:
        log.exception(f"Keystone error: {err}")
        return render(request, "vault/swift_cloud/status.html",
            {"projects": [], "error": "Keystone Error"})

    environ = settings.ENVIRON
    if not environ and "localhost" in request.get_host():
        environ = "local"

    user = request.user
    group_ids = [g.id for g in user.groups.all()]
    projects = []
    keystone_projects = keystone.project_list()

    try:
        group_projects = GroupProjects.objects.filter(
            group_id__in=group_ids, owner=True)
        for project in keystone_projects:
            for gp in group_projects:
                if project.id == gp.project:
                    projects.append({
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "environment": environ,
                        "team": gp.group.name,
                        "status": "",
                        "metadata": {}
                    })
        projects.sort(key=lambda p: p["name"].lower())
    except Exception as err:
        log.exception(f"Keystone error: {err}")

    # Get transfer status for all projects in swift cloud tools api
    sct_client = SCTClient(settings.SWIFT_CLOUD_TOOLS_URL,
                           settings.SWIFT_CLOUD_TOOLS_API_KEY)
    data = []
    try:
        response = sct_client.transfer_status_by_projects(
            [p["id"] for p in projects])
        if reponse and reponse.status_code == 200:
            data = response.json()
    except Exception as err:
        log.exception(f"Swift Cloud Tools Error: {err}")

    return render(request, "vault/swift_cloud/status.html", {
        "projects": json.dumps(projects),
        "migration_data": json.dumps(data)
    })


@login_required
def swift_cloud_project_status(request):
    project_id = request.GET.get('project_id')

    if not project_id:
        raise Http404

    try:
        keystone = Keystone(request)
        project = keystone.project_get(project_id)
    except Exception as err:
        log.exception(f"Keystone error: {err}")
        return render(request, "vault/swift_cloud/project_status.html",
            {"project": None,
             "error": "Keystone Error"})

    sct_client = SCTClient(settings.SWIFT_CLOUD_TOOLS_URL,
                           settings.SWIFT_CLOUD_TOOLS_API_KEY)
    status = ""
    data = {}

    try:
        response = sct_client.transfer_get(project_id)
        if reponse and reponse.status_code == 200:
            data = response.json()
        else:
            status = _("Couldn't get migration data")
    except Exception as err:
        log.exception(f"Swift Cloud Tools Error: {err}")

    if response.status_code == 404:
        status = _("Migration not initialized yet")

    if response.status_code < 300:
        status = _("Waiting in migration queue")

    if data.get("initial_date") and not data.get("final_date"):
        status = _("Migrating...")

    if data.get("final_date"):
        status = _("Migration Completed")

    http_conn, storage_url = get_conn_and_storage_url(request, project_id)
    auth_token = request.session.get('auth_token')
    head_account = {}

    try:
        head_account = client.head_account(storage_url,
            auth_token, http_conn=http_conn)
    except Exception as err:
        log.exception(f'Exception: {err}')

    if head_account.get("x-account-meta-cloud-remove"):
        status = _("Marked for removal")

    return render(request, "vault/swift_cloud/project_status.html", {
        "project": project,
        "status": status,
        "metadata": json.dumps(head_account),
        "migration_data": json.dumps(data)
    })


@login_required
def swift_cloud_migrate(request):
    if request.method != 'POST':
        return JsonResponse({"error": _("Method not allowed")}, status=405)

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY)

    params = json.loads(request.body)
    content = {"message": _("Migration job created")}
    status = 201

    response = sct_client.transfer_create(
        params.get('project_id'),
        params.get('project_name'),
        params.get('environment'))

    status = response.status_code

    if status != 201:
        content = {"error": response.text}

    return JsonResponse(content, status=status)


@login_required
def swift_cloud_removal(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    params = json.loads(request.body)
    project_id = params.get('project_id')
    undo_removal = params.get('undo_removal')

    if not project_id:
        return JsonResponse({"error": "Missing project_id parameter"}, status=400)

    http_conn, storage_url = get_conn_and_storage_url(request, project_id)
    auth_token = request.session.get('auth_token')
    headers = {"x-account-meta-cloud-remove": "true"}

    if undo_removal:
        headers["x-account-meta-cloud-remove"] = ""

    try:
        client.post_account(storage_url, auth_token,
            headers, http_conn=http_conn)
    except Exception as err:
        log.exception(f'Exception: {err}')
        return JsonResponse({"error": "Project update error"}, status=500)

    return JsonResponse({"message": "Success"}, status=200)


@login_required
def swift_cloud_price_preview(request):
    amount = request.GET.get('amount')

    if not amount:
        return JsonResponse(
            {"error": "Missing amount parameter"}, status=400)

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY)

    response = sct_client.billing_get_price_from_service(
        settings.SWIFT_CLOUD_GCP_SERVICE_ID,
        settings.SWIFT_CLOUD_GCP_SKU,
        int(amount))

    result = {"price": None, "currency": None}
    status = 500

    if reponse and reponse.status_code == 200:
        result = response.json()
        status = 200

    return JsonResponse(result, status=status)
