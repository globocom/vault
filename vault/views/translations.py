import json
from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required


@login_required
def js(request):
    translations = {
        "add": _("Add"),
        "addNewUser": _("Add new user"),
        "addNewUserTeam": _("Add new user to this team"),
        "addTo": _("Add to"),
        "cancel": _("Cancel"),
        "clear": _("Clear"),
        "containers": _("Containers"),
        "currency": _("Currency"),
        "details": _("Details"),
        "done": _("Done"),
        "estimatedCloudPrice": _("Estimated Cloud Price"),
        "filterUsers": _("Filter users within each team"),
        "hasBeenMarkedRemoval": _("This project has been marked for removal"),
        "markedForRemoval": _("Marked for removal"),
        "migratedData": _("Migrated Data"),
        "migratedProjects": _("Migrated projects"),
        "migrateProject": _("Migrate this project"),
        "migrating": _("Migrating..."),
        "migrationCompleted": _("Migration Completed"),
        "migrationInfo": _("Migration Info"),
        "migrationStatus": _("Migration Status"),
        "monthly": _("Monthly"),
        "myTeams": _("My Teams"),
        "objects": _("Objects"),
        "project": _("Project"),
        "projectId": _("Project ID"),
        "projectName": _("Project Name"),
        "projectRemovalMsg": _("The project will be marked for removal. Confirm?"),
        "projectsMarkedForRemoval": _("Projects marked for removal"),
        "removeProject": _("Remove this project"),
        "removeUser": _("Remove user"),
        "removeUserWarning": _("The user will lose access to all projects owned by this team! Continue?"),
        "selectUser": _("Select a user"),
        "startMigrationMsg": _("This will start the migration. Confirm?"),
        "swiftData": _("Swift Data"),
        "team": _("Team"),
        "teams": _("Teams"),
        "totalBytes": _("Total bytes"),
        "totalProjects": _("Total projects"),
        "totalUsedSpace": _("Total Used Space"),
        "undoRemovalMsg": _("This will undo the removal of this project. Continue?"),
        "undoRemoveProject": _("Undo Project Removal"),
        "user": _("User"),
        "userAdded": _("User added"),
        "userRemoved": _("User removed"),
        "users":  _("Users"),
        "waitingMigration": _("Waiting in migration queue"),
    }

    return HttpResponse(
        f"const TRANSLATIONS = {json.dumps(translations)}",
        content_type="application/javascript"
    )
