# -*- coding: utf-8 -*-

from django.conf.urls import url
from swiftbrowser import views


urlpatterns = [
    url(r'^backup-list/?', views.container_backup_list, name="container_backup_list"),
]
