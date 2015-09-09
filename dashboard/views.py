# -*- coding: utf-8 -*-

from django.views.generic.base import TemplateView

from vault.views import LoginRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
