# -*- coding:utf-8 -*-

from django.conf.urls import patterns, url

from identity import views


urlpatterns = patterns('',
    # Admin
    url(r'^admin/projects/$', views.ListProjectView.as_view(), name='projects'),
    url(r'^admin/project/add/?$', views.CreateProjectView.as_view(), name='add_project'),
    url(r'^admin/project/(?P<project_id>[\w\-]+)/?$', views.UpdateProjectView.as_view(),
       name='edit_project'),

    # Users
    url(r'^users/?$', views.ListUserView.as_view(), name='users'),
    url(r'^user/add/?$', views.CreateUserView.as_view(), name='add_user'),
    url(r'^user/(?P<user_id>[\w\-]+)/?$', views.UpdateUserView.as_view(),
       name='edit_user'),
    url(r'^user/delete/(?P<user_id>[\w\-]+)/?$', views.DeleteUserView.as_view(),
       name='delete_user'),

    # Projects
    url(r'^projects/', views.ListProjectView.as_view(), name='projects'),
    url(r'^project/add/?$', views.CreateProjectView.as_view(), name='add_project'),
    url(r'^project/created/?$', views.CreateProjectSuccessView.as_view(),
       name='create_project_success'),
    url(r'^project/(?P<project_id>[\w\-]+)/?$', views.UpdateProjectView.as_view(),
       name='edit_project'),
    url(r'^project/delete/(?P<project_id>[\w\-]+)/?$', views.DeleteProjectView.as_view(),
       name='delete_project'),

    # Ajax
    url(r'^project-add-user/?$', views.AddUserRoleView.as_view(),
       name='project_add_user'),
    url(r'^project-delete-user/?$', views.DeleteUserRoleView.as_view(),
       name='project_delete_user'),
    url(r'^project-list-users/?$', views.ListUserRoleView.as_view(),
       name='project_list_users'),
)
