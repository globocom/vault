import json
import logging

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from identity.keystone import Keystone
from vault.utils import update_default_context

log = logging.getLogger(__name__)


@login_required
def swift_cloud_report(request):
    keystone = Keystone(request)
    projects = []

    try:
        for project in keystone.project_list():
            projects.append({
                "id": project.id,
                "name": project.name,
                "description": project.description
            })
    except Exception as e:
        log.exception(f"Keystone error: {e}")

    context = {"projects": json.dumps(projects)}

    return render(request, "vault/swift_cloud/report.html", context)
