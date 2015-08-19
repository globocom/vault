# -*- coding:utf-8 -*-

import logging

from django.views.generic.base import TemplateView

from vault.views import LoginRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def __init__(self, *args, **kwargs):
        self.keystone = None
        return super(DashboardView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        return context


