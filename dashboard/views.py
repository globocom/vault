# -*- coding: utf-8 -*-

from django.apps import apps
from django.views.generic.base import TemplateView
from django.shortcuts import render_to_response

from vault.views import LoginRequiredMixin, ProjectCheckMixin


class DashboardView(LoginRequiredMixin, ProjectCheckMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get(self, request, *args, **kwargs):

        info_endpoints = []

        for conf in apps.get_app_configs():
            if hasattr(conf, 'info_endpoint'):
                info_endpoints.append(conf.info_endpoint)

        context = {
            "info_endpoints": info_endpoints
        }

        return self.render_to_response(context)
