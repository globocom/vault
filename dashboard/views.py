# -*- coding: utf-8 -*-

from django.views.generic.base import TemplateView

from vault.views import LoginRequiredMixin, ProjectCheckMixin


class DashboardView(LoginRequiredMixin, ProjectCheckMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
