from django.apps import apps
from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, re_path
from django.utils.translation import gettext_lazy as _

from identity.views import CreateProjectView, ChangeProjectView

from vault import views
from vault.forms import VaultLoginForm

admin.site.index_title = _("Admin Dashboard")


urlpatterns = [
    # overwrite admin:login
    re_path(r"^admin/login/$", views.VaultLogin.as_view(authentication_form=VaultLoginForm), name="vault_login"),

    # overwrite admin:logout (need to be before admin urls)
    re_path(r"^admin/logout/$", views.VaultLogout.as_view(), name="vault_logout"),

    # OAuthCallback
    re_path(r"^accounts/callback/(?P<provider>[\w\-]+)/$", views.OAuthVaultCallback.as_view(), name="allaccess-callback"),

    # OAuthLogin
    re_path(r"^accounts/login/(?P<provider>[\w\-]+)/$", views.OAuthVaultRedirect.as_view(), name="allaccess-login"),

    # OAuth
    re_path(r"^accounts/", include("allaccess.urls")),

    # Admin
    re_path(r"^admin/", admin.site.urls),

    # Team CRUD
    re_path(r"^team/add/user/?$", views.AddUserTeamView.as_view(), name="team_add_user"),
    re_path(r"^team/delete/user/?$", views.DeleteUserTeamView.as_view(), name="team_delete_user"),
    re_path(r"^team/list/users/?$", views.ListUserTeamView.as_view(), name="team_list_users"),
    re_path(r"^p/(?P<project>.+?)/team/update/users/?$", views.UpdateTeamsUsersView.as_view(), name="update_teams_users"),

    # Team List
    re_path(r"^p/(?P<project>.+?)/team-users/?$", views.ListUsersTeamsView.as_view(), name="team_users"),

    # Project
    re_path(r"^project/add/?$", CreateProjectView.as_view(), name="add_project"),
    re_path(r"^project/change/?$", ChangeProjectView.as_view(), name="change_project"),
    re_path(r"^project/(?P<project_id>[\w\-]+)/set/?$", views.SetProjectView.as_view(), name="set_project"),

    # Team Manage
    re_path(r"^p/(?P<project>.+?)/team/manage/?$", views.team_manager_view, name="team_manage"),
    re_path(r"^p/(?P<project>.+?)/team/manage/outsideusers/?$", views.list_users_outside_a_group, name="outside_users"),

    # Apps Info
    re_path(r"^apps/info", views.apps_info, name="apps_info"),
]


# Swift Cloud
if settings.SWIFT_CLOUD_ENABLED:
    urlpatterns.append(re_path(r"^swift-cloud/report/?$", views.swift_cloud_report, name="swift_cloud_report"))
    urlpatterns.append(re_path(r"^swift-cloud/status/?$", views.swift_cloud_status, name="swift_cloud_status"))
    urlpatterns.append(re_path(r"^swift-cloud/migrate/?$", views.swift_cloud_migrate, name="swift_cloud_migrate"))


for app in apps.app_configs:
    if "vault_app" in dir(apps.app_configs[app]):
        urlpatterns.append(re_path(rf"^p/(?P<project>.+?)/{app}/", include(f"{app}.urls")))


urlpatterns.append(re_path(r"^p/(?P<project>.+?)/", views.DashboardView.as_view(), name="dashboard"))
urlpatterns.append(re_path(r"^", views.main_page, name="main"))
