# -*- coding: utf-8 -*-

from django.apps import apps
from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.utils.translation import gettext_lazy as _

from identity.views import CreateProjectView, ChangeProjectView

from vault import views
from vault.forms import VaultLoginForm

admin.site.index_title = _("Admin Dashboard")


urlpatterns = [
    # overwrite admin:login
    url(r"^admin/login/$", views.VaultLogin.as_view(authentication_form=VaultLoginForm), name="vault_login"),

    # overwrite admin:logout (need to be before admin urls)
    url(r"^admin/logout/$", views.VaultLogout.as_view(), name="vault_logout"),

    # OAuthCallback
    url(r"^accounts/callback/(?P<provider>[\w\-]+)/$", views.OAuthVaultCallback.as_view(), name="allaccess-callback"),

    # OAuthLogin
    url(r"^accounts/login/(?P<provider>[\w\-]+)/$", views.OAuthVaultRedirect.as_view(), name="allaccess-login"),

    # OAuth
    url(r"^accounts/", include("allaccess.urls")),

    # Admin
    url(r"^admin/", admin.site.urls),

    # Team CRUD
    url(r"^team/add/user/?$", views.AddUserTeamView.as_view(), name="team_add_user"),
    url(r"^team/delete/user/?$", views.DeleteUserTeamView.as_view(), name="team_delete_user"),
    url(r"^team/list/users/?$", views.ListUserTeamView.as_view(), name="team_list_users"),
    url(r"^p/(?P<project>.+?)/team/update/users/?$", views.UpdateTeamsUsersView.as_view(), name="update_teams_users"),

    # Team List
    url(r"^p/(?P<project>.+?)/team-users/?$", views.ListUsersTeamsView.as_view(), name="team_users"),

    # Project
    url(r"^project/add/?$", CreateProjectView.as_view(), name="add_project"),
    url(r"^project/change/?$", ChangeProjectView.as_view(), name="change_project"),
    url(r"^project/(?P<project_id>[\w\-]+)/set/?$", views.SetProjectView.as_view(), name="set_project"),

    # Team Manage
    url(r"^p/(?P<project>.+?)/team/manage/?$", views.team_manager_view, name="team_manage"),
    url(r"^p/(?P<project>.+?)/team/manage/outsideusers/?$", views.list_users_outside_a_group, name="outside_users"),
]


# Swift Cloud
if settings.SWIFT_CLOUD_ENABLED:
    urlpatterns.append(url(r"^swift-cloud/report/?$", views.swift_cloud_report, name="swift_cloud_report"))
    urlpatterns.append(url(r"^swift-cloud/status/?$", views.swift_cloud_status, name="swift_cloud_status"))
    urlpatterns.append(url(r"^swift-cloud/migrate/?$", views.swift_cloud_migrate, name="swift_cloud_migrate"))


for app in apps.app_configs:
    if "vault_app" in dir(apps.app_configs[app]):
        urlpatterns.append(url(rf"^p/(?P<project>.+?)/{app}/", include(f"{app}.urls")))


urlpatterns.append(url(r"^p/(?P<project>.+?)/", views.DashboardView.as_view(), name="dashboard"))
urlpatterns.append(url(r"^", views.main_page, name="main"))
