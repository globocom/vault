import json
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required


@login_required
def js(request):
    translations = {
        "startMigrationMsg": _("This will start the migration. Confirm?"),
        "projectRemovalMsg": _("The project will be marked for removal. Confirm?"),
        "undoRemovalMsg": _("This will undo the removal of this project. Continue?"),
        "project": _("Project"),
        "projectId": _("Project ID"),
        "projectName": _("Project Name"),
        "migrationStatus": _("Migration Status"),
        "migrateProject": _("Migrate this project"),
        "removeProject": _("Remove this project"),
        "undoRemoveProject": _("Undo Project Removal"),
        "swiftData": _("Swift Data"),
        "objects": _("Objects"),
        "totalBytes": _("Total bytes"),
        "migratedData": _("Migrated Data"),
        "migrationInfo": _("Migration Info"),
        "waitingMigration": _("Waiting in migration queue"),
        "migrating": _("Migrating..."),
        "done": _("Done"),
        "details": _("Details"),
        "totalProjects": _("Total projects"),
        "migratedProjects": _("Migrated projects"),
        "team": _("Team"),
    }

    return HttpResponse(
        f"const TRANSLATIONS = {json.dumps(translations)}",
        content_type="application/javascript"
    )
