# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

from identity.views import (ListUserView, ListProjectView, CreateUserView,
    UpdateUserView, DeleteUserView, CreateProjectView, UpdateProjectView,
    DeleteProjectView, ListUserRoleView, AddUserRoleView, DeleteUserRoleView)


urlpatterns = patterns('',
    # Admin
   url(r'^admin/projects/$', ListProjectView.as_view(), name='projects'),
   url(r'^admin/project/add/?$', CreateProjectView.as_view(), name='add_project'),
   url(r'^admin/project/(?P<project_id>[\w\-]+)/?$', UpdateProjectView.as_view(), name='edit_project'),

    # Users
    url(r'^users/?$', ListUserView.as_view(), name='users'),
    url(r'^user/add/?$', CreateUserView.as_view(), name='add_user'),
    url(r'^user/(?P<user_id>[\w\-]+)/?$', UpdateUserView.as_view(),
        name='edit_user'),
    url(r'^user/delete/(?P<user_id>[\w\-]+)/?$', DeleteUserView.as_view(),
        name='delete_user'),

    # Projects
    url(r'^projects/', ListProjectView.as_view(), name='projects'),
    url(r'^project/add/?$', CreateProjectView.as_view(), name='add_project'),
    url(r'^project/(?P<project_id>[\w\-]+)/?$', UpdateProjectView.as_view(),
        name='edit_project'),
    url(r'^project/delete/(?P<project_id>[\w\-]+)/?$', DeleteProjectView.as_view(),
        name='delete_project'),

    # Ajax
    url(r'^project-add-user/?$', AddUserRoleView.as_view(),
        name='project_add_user'),
    url(r'^project-delete-user/?$', DeleteUserRoleView.as_view(),
        name='project_delete_user'),
    url(r'^project-list-users/?$', ListUserRoleView.as_view(),
        name='project_list_users'),
)
