# -*- coding: utf-8 -*-

from django.conf.urls import url

from identity import views


urlpatterns = [
    # Admin Users Keystone
    url(r"^users/?$", views.ListUserView.as_view(), name="admin_list_users"),
    url(r"^user/add/?$", views.CreateUserView.as_view(), name="admin_add_user"),
    url(r"^user/(?P<user_id>[\w\-]+)/?$", views.UpdateUserView.as_view(), name="edit_user"),
    url(r"^user/delete/(?P<user_id>[\w\-]+)/?$", views.DeleteUserView.as_view(), name="delete_user"),
    # Ajax
    url(r"^project-add-user/?$", views.AddUserRoleView.as_view(), name="project_add_user"),
    url(r"^project-delete-user/?$", views.DeleteUserRoleView.as_view(), name="project_delete_user"),
    url(r"^project-list-users/?$", views.ListUserRoleView.as_view(), name="project_list_users"),
    # ===============================================================================================
    # Project
    url(r"^projects/", views.ListProjectView.as_view(), name="projects"),
    url(r"^project/created/?$", views.CreateProjectSuccessView.as_view(), name="create_project_success"),
    url(r"^project/(?P<project_id>[\w\-]+)/?$", views.UpdateProjectView.as_view(), name="edit_project"),
    url(r"^project/delete/(?P<project_id>[\w\-]+)/?$", views.DeleteProjectView.as_view(), name="delete_project"),
    # Update User Password
    url(r"^project/user/updatepass/?$", views.UpdateProjectUserPasswordView.as_view(), name="update_pass"),
    # ===============================================================================================
    # API
    url(r"^api/info$", views.JsonInfoView.as_view(), name="info_json"),
]
