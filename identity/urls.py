# -*- coding: utf-8 -*-

from django.conf.urls import url

from identity import views


urlpatterns = [
    # Project
    url(r'^projects/', views.ListProjectView.as_view(), name='projects'),
    url(r'^project/add/?$', views.CreateProjectView.as_view(), name='add_project'),
    url(r'^project/created/?$', views.CreateProjectSuccessView.as_view(), name='create_project_success'),
    url(r'^project/(?P<project_id>[\w\-]+)/?$', views.UpdateProjectView.as_view(), name='edit_project'),
    url(r'^project/delete/(?P<project_id>[\w\-]+)/?$', views.DeleteProjectView.as_view(), name='delete_project'),

    # JSON info
    url(r'^info$', views.JsonInfoView.as_view(), name="info_json"),

    # Update User Password
    url(r'^project/user/updatepass/?$', views.UpdateProjectUserPasswordView.as_view(), name='update_pass'),
]
