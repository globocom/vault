import json
import logging
import requests
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from identity.keystone import Keystone

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

    url = f"{settings.SWIFT_CLOUD_TOOLS_URL}/transfer/{project_id}"
    headers = {"X-Auth-Token": settings.SWIFT_CLOUD_TOOLS_API_KEY}
    content = {"status": None}

    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        if res.status_code == 404:
            content["status"] = "Not initialized"
        else:
            content["status"] = "Waiting"

        if data.get("initial_date") and not data.get("final_date"):
            content["status"] = "Migrating"

        if data.get("final_date"):
            content["status"] = "Done"
    except Exception as err:
        log.error(err)

    return JsonResponse(content, status=200)


@login_required
def swift_cloud_migrate(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    url = f"{settings.SWIFT_CLOUD_TOOLS_URL}/transfer/"
    headers = {"X-Auth-Token": settings.SWIFT_CLOUD_TOOLS_API_KEY}
    params = json.loads(request.body)
    content = {"message": "Migration job created"}
    status = 201

    try:
        res = requests.post(url, json=params, headers=headers)
        status = res.status_code
        if status != 201:
            content = {"error": res.text}
    except Exception as err:
        log.error(err)
        content = {"error": err}

    return JsonResponse(content, status=status)
