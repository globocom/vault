from ipaddress import ip_address
import json
import logging
import pdb
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from identity.keystone import Keystone
from vault.models import GroupProjects
from swift_cloud_tools.client import SCTClient

log = logging.getLogger(__name__)


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

    res = sct_client.transfer_status_by_projects(
        [p["id"] for p in projects])
    data = res.json()

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
                    })
        projects.sort(key=lambda p: p["name"].lower())
    except Exception as err:
        log.exception(f"Keystone error: {err}")

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY
    )

    res = sct_client.transfer_status_by_projects(
        [p["id"] for p in projects])
    data = res.json()

    return render(request, "vault/swift_cloud/status.html",
        {"projects": json.dumps(projects),
         "migration_data": json.dumps(data)})


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

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY
    )

    status = None
    response = sct_client.transfer_get(project_id)
    data = response.json()

    if response.status_code == 404:
        status = _("Migration not initialized yet")
    else:
        status = _("Waiting in migration queue")

    if data.get("initial_date") and not data.get("final_date"):
        status = _("Migrating...")

    if data.get("final_date"):
        status = _("Done")

    return render(request, "vault/swift_cloud/project_status.html",
        {"project": project,
         "status": status,
         "migration_data": json.dumps(data)})


@login_required
def swift_cloud_migrate(request):
    if request.method != 'POST':
        return JsonResponse({"error": _("Method not allowed")}, status=405)

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY
    )
    params = json.loads(request.body)
    content = {"message": _("Migration job created")}
    status = 201

    response = sct_client.transfer_create(
        params.get('project_id'),
        params.get('project_name'),
        params.get('environment')
    )
    status = response.status_code
    if status != 201:
        content = {"error": response.text}

    return JsonResponse(content, status=status)
