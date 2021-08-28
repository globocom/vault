from django.conf.urls import re_path
from identity import views


urlpatterns = [
    # Admin Users Keystone
    re_path(r"^users/?$", views.ListUserView.as_view(), name="admin_list_users"),
    re_path(r"^user/add/?$", views.CreateUserView.as_view(), name="admin_add_user"),
    re_path(r"^user/(?P<user_id>[\w\-]+)/?$", views.UpdateUserView.as_view(), name="edit_user"),
    re_path(r"^user/delete/(?P<user_id>[\w\-]+)/?$", views.DeleteUserView.as_view(), name="delete_user"),

    # Ajax
    re_path(r"^project-add-user/?$", views.AddUserRoleView.as_view(), name="project_add_user"),
    re_path(r"^project-delete-user/?$", views.DeleteUserRoleView.as_view(), name="project_delete_user"),
    re_path(r"^project-list-users/?$", views.ListUserRoleView.as_view(), name="project_list_users"),

    # Project
    re_path(r"^projects/", views.ListProjectView.as_view(), name="projects"),
    re_path(r"^project/created/?$", views.CreateProjectSuccessView.as_view(), name="create_project_success"),
    re_path(r"^project/(?P<project_id>[\w\-]+)/?$", views.UpdateProjectView.as_view(), name="edit_project"),
    re_path(r"^project/delete/(?P<project_id>[\w\-]+)/?$", views.DeleteProjectView.as_view(), name="delete_project"),

    # Update User Password
    re_path(r"^project/user/updatepass/?$", views.UpdateProjectUserPasswordView.as_view(), name="update_pass"),

    # API
    re_path(r"^api/info$", views.JsonInfoView.as_view(), name="info_json"),
]
