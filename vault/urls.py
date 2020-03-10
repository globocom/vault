# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import gettext as _
from django.conf.urls import include, url
from django.apps import apps

from identity.views import ListProjectView, CreateProjectView

from vault import views

admin.site.index_title = _("Admin Dashboard")


urlpatterns = [

    # sobreescrevendo admin:login
    url(r'^admin/login/$', views.VaultLogin.as_view(), name='vault_login'),

    # sobreescrevendo admin:logout devido ao redirect loop gerado pelo
    # backstage_accounts (precisa ficar antes das urls do admin)
    url(r'^admin/logout/$', views.VaultLogout.as_view(), name='vault_logout'),

    # OAuthCallback
    url(r'^accounts/callback/(?P<provider>[\w\-]+)/$', views.OAuthVaultCallback.as_view(), name='allaccess-callback'),

    # OAuthLogin
    url(r'^accounts/login/(?P<provider>[\w\-]+)/$', views.OAuthVaultRedirect.as_view(), name='allaccess-login'),

    # OAuth
    url(r'^accounts/', include('allaccess.urls')),

    # Admin
    url(r'^admin/', admin.site.urls),

    # Team CRUD
    url(r'^team/add/user/?$', views.AddUserTeamView.as_view(), name='team_add_user'),
    url(r'^team/delete/user/?$', views.DeleteUserTeamView.as_view(), name='team_delete_user'),
    url(r'^team/list/users/?$', views.ListUserTeamView.as_view(), name='team_list_users'),
    url(r'^team/update/users/?$', views.UpdateTeamsUsersView.as_view(), name='update_teams_users'),

    # Team List
    url(r'^team-users/?$', views.ListUsersTeamsView.as_view(), name='team_users'),

    # Team Manage
    url(r'^team/manage/?$', views.team_manager_view, name='team_manage'),
    url(r'^team/manage/outsideusers/?$', views.list_users_outside_a_group, name='outside_users'),

    # set project_id session
    url(r'^set-project/(?P<project_id>[\w\-]+)/?$', views.SetProjectView.as_view(), name='set_project'),

    # Project
    url(r'^project/?$', ListProjectView.as_view(), name='projects'),
    url(r'^project/add/?$', CreateProjectView.as_view(), name='add_project'),

]

for app in apps.app_configs:
    if 'vault_app' in dir(apps.app_configs[app]):
        urlpatterns.append(url(rf'^p/(?P<project>.+?)?/{app}/', include(f'{app}.urls')))

urlpatterns.append(url(r'^p/(?P<project>.+?)?/', views.DashboardView.as_view(), name='dashboard'))
urlpatterns.append(url(r'^', views.main_page, name='main'))
