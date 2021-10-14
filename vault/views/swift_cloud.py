import json
import logging
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from identity.keystone import Keystone
from swift_cloud_tools.client import SCTClient

log = logging.getLogger(__name__)


@login_required
def swift_cloud_report(request):
    keystone = Keystone(request)
    projects = []
    environ = settings.ENVIRON

    if not environ and "localhost" in request.get_host():
        environ = "local"

    try:
        for project in keystone.project_list():
            projects.append({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "environment": environ,
                "status": "",
            })
    except Exception as e:
        log.exception(f"Keystone error: {e}")

    context = {"projects": json.dumps(projects)}

    return render(request, "vault/swift_cloud/report.html", context)


@login_required
def swift_cloud_status(request):
    project_id = request.GET.get('project_id')

    if not project_id:
        return JsonResponse({"error": "Missing project_id parameter"}, status=400)

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY
    )
    content = {"status": None}

    response = sct_client.transfer_get(project_id)
    data = response.json()

    if response.status_code == 404:
        content["status"] = "Not initialized"
    else:
        content["status"] = "Waiting"

    if data.get("initial_date") and not data.get("final_date"):
        content["status"] = "Migrating"

    if data.get("final_date"):
        content["status"] = "Done"

    return JsonResponse(content, status=200)


@login_required
def swift_cloud_migrate(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    sct_client = SCTClient(
        settings.SWIFT_CLOUD_TOOLS_URL,
        settings.SWIFT_CLOUD_TOOLS_API_KEY
    )
    params = json.loads(request.body)
    content = {"message": "Migration job created"}
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
