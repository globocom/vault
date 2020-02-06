# -*- coding: utf-8 -*-

from django.views.generic.base import TemplateView

from vault.views import LoginRequiredMixin, ProjectCheckMixin


class DashboardView(LoginRequiredMixin, ProjectCheckMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get(self, request, *args, **kwargs):

        context = {
            "has_team": request.user.groups.count() > 0
        }

        return self.render_to_response(context)
