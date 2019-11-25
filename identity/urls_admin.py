# -*- coding: utf-8 -*-

from django.conf.urls import url

from identity import views


urlpatterns = [
    # Admin Project Keystone
    url(r'^projects/$', views.ListProjectView.as_view(), name='admin_projects'),
    url(r'^project/add/?$', views.CreateProjectView.as_view(), name='admin_add_project'),
    url(r'^project/(?P<project_id>[\w\-]+)/?$', views.UpdateProjectView.as_view(), name='admin_edit_project'),

    # Admin Users Keystone
    url(r'^users/?$', views.ListUserView.as_view(), name='admin_list_users'),
    url(r'^user/add/?$', views.CreateUserView.as_view(), name='admin_add_user'),
    url(r'^user/(?P<user_id>[\w\-]+)/?$', views.UpdateUserView.as_view(), name='edit_user'),
    url(r'^user/delete/(?P<user_id>[\w\-]+)/?$', views.DeleteUserView.as_view(), name='delete_user'),

    # Ajax
    url(r'^project-add-user/?$', views.AddUserRoleView.as_view(), name='project_add_user'),
    url(r'^project-delete-user/?$', views.DeleteUserRoleView.as_view(), name='project_delete_user'),
    url(r'^project-list-users/?$', views.ListUserRoleView.as_view(), name='project_list_users'),
]
