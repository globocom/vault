# -*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from dashboard.views import DashboardView


urlpatterns = patterns('',
    url(r'^/?$', DashboardView.as_view(), name='dashboard'),
)
