# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext as _
from django.conf.urls import include, url

from vault import views

admin.site.index_title = _("Admin Dashboard")


urlpatterns = [
    # Admin
    url(r'^admin/', admin.site.urls),

    # Identity admin
    url(r'^admin/identity/', include('identity.urls_admin')),

    # Identity
    url(r'^identity/', include('identity.urls')),

    # Swift
    url(r'^storage/', include('swiftbrowser.urls')),
    url(r'^api/storage/', include('swiftbrowser.api_urls')),

    # Team CRUD
    url(r'^team/add/user/?$', views.AddUserTeamView.as_view(), name='team_add_user'),
    url(r'^team/delete/user/?$', views.DeleteUserTeamView.as_view(), name='team_delete_user'),
    url(r'^team/list/users/?$', views.ListUserTeamView.as_view(), name='team_list_users'),
    url(r'^team/update/users/?$', views.UpdateTeamsUsersView.as_view(), name='update_teams_users'),

    # Team List OGs
    url(r'^team/list/users/ogs/?$', views.ListUsersTeamsOGsView.as_view(), name='team_list_users_ogs'),

    # Team Manage
    url(r'^team/manage/?$', views.team_manager_view, name='team_manage'),
    url(r'^team/manage/outsideusers/?$', views.list_users_outside_a_group, name='outside_users'),

    # set project_id session
    url(r'^set-project/(?P<project_id>[\w\-]+)/?$', views.SetProjectView.as_view(), name='set_project'),

    # Dashboard
    url(r'^', include('dashboard.urls')),
]
