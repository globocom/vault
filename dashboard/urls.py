# -*- coding: utf-8 -*-

from django.conf.urls import url
from dashboard.views import DashboardView


urlpatterns = [
    url(r'^#noproject$', DashboardView.as_view(), name='dashboard_noproject'),
    url(r'^', DashboardView.as_view(), name='dashboard'),
]
