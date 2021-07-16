# -*- coding: utf-8 -*-

"""
Vault Generic Views
"""

import json
import logging
from hashlib import md5

from django.contrib import messages
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.views import LoginView

from keystoneclient import exceptions

from allaccess.models import Provider
from allaccess.views import OAuthCallback, OAuthRedirect

from actionlogger.actionlogger import ActionLogger
from identity.keystone import Keystone
from vault.models import GroupProjects
from vault.utils import (
    update_default_context,
    save_current_project,
    set_current_project,
    get_current_project,
    maybe_update_token,
    project_required,
)

from vault.client import OAuth2BearerClient

log = logging.getLogger(__name__)
actionlog = ActionLogger()


def _build_next_url(request):
    next_url = request.META.get("HTTP_REFERER")

    if request.GET.get("next") is not None:
        next_url = request.GET.get("next")

    if next_url:
        return next_url

    return reverse("main")


def switch(request, project_id):
    """Switch session parameters to project with project_id"""

    if project_id is None:
        raise ValueError(_("Missing 'project_id'"))

    next_url = reverse("main")  # _build_next_url(request)

    try:
        keystone = Keystone(request)
    except exceptions.AuthorizationFailure:
        msg = _("Unable to retrieve Keystone data")
        messages.add_message(request, messages.ERROR, msg)
        log.error(f"{request.user}: {msg}")

        return HttpResponseRedirect(next_url)

    try:
        project = keystone.project_get(project_id)
    except Exception as err:
        messages.add_message(request, messages.ERROR, _("Can't find this project"))
        log.exception("{}{}".format(_("Exception:").encode("UTF-8"), err))
        return HttpResponseRedirect(next_url)

    save_current_project(request.user.id, project.id)
    set_current_project(request, project)

    log.info("User [{}] switched to project [{}]".format(request.user, project_id))
    messages.add_message(request, messages.INFO, _("Project selected: {}".format(project.name)))

    return HttpResponseRedirect(next_url)


class ProjectCheckMixin:
    """Mixin for Views to check and set user current project"""

    @method_decorator(project_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectCheckMixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin:
    """Mixin for Class Views that needs a user login"""

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        maybe_update_token(request)
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginRequiredMixin, self).get_context_data(**kwargs)
        return update_default_context(self.request, context)


class SuperUserMixin(LoginRequiredMixin):
    """Mixin for Class Views with superuser powers"""

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            messages.add_message(self.request, messages.WARNING, "Unauthorized")
            return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

        return super(SuperUserMixin, self).dispatch(request, *args, **kwargs)


class JSONResponseMixin:
    """Mixin for Class Views with json response"""

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(self.convert_context_to_json(context), content_type="application/json", **response_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)


class SetProjectView(LoginRequiredMixin, View):
    """Change user current project"""

    def get(self, request, *args, **kwargs):
        request.session["project_id"] = kwargs.get("project_id")

        try:
            http_redirect = switch(request, kwargs.get("project_id"))
        except ValueError as err:
            http_redirect = HttpResponseRedirect(reverse("main"))
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), err))
            messages.add_message(request, messages.ERROR, _("Unable to change your project."))

        return http_redirect


class DashboardView(LoginRequiredMixin, ProjectCheckMixin, TemplateView):
    template_name = "vault/dashboard.html"

    def get(self, request, *args, **kwargs):

        context = update_default_context(
            request,
            {
                "project_name": request.session.get("project_name"),
                "project_id": request.session.get("project_id"),
                "has_team": request.user.groups.count() > 0,
                "last_login": str(request.user.last_login),
            },
        )

        return self.render_to_response(context)


class VaultLogin(LoginView):
    template_name = "vault/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        providers = []

        for provider in Provider.objects.all():
            providers.append({
                "name": provider.name,
                "url": reverse("allaccess-login", kwargs={"provider": provider.name})
            })

        context.update({
            "providers": providers,
            "username": user.get_username()
        })

        return context


class VaultLogout(View):

    def get(self, request):
        user = request.user
        logout(request)
        log.info(_("User logged out:") + " [{}]".format(user))
        return HttpResponseRedirect(reverse("main"))


def handler500(request):
    response = render(request, "500.html", {})
    response.status_code = 500

    return response


class UpdateTeamsUsersView(LoginRequiredMixin, FormView):
    template_name = "vault/user_edit_teams.html"

    def get(self, request, *args, **kwargs):
        context = {}
        context["users"] = []
        context["groups"] = []

        try:
            all_groups_id = [group.id for group in Group.objects.all()]

            # Users without a team
            users = User.objects.exclude(groups__in=all_groups_id).order_by("username")

            for user in User.objects.all().order_by("username"):
                context["users"].append({"id": int(user.id), "name": user.username})

            for grp in request.user.groups.all():
                context["groups"].append({"id": int(grp.id), "name": grp.name})

            context = update_default_context(request, context)

        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return self.render_to_response(context, status=500)

        return self.render_to_response(context)


class ListUserTeamView(LoginRequiredMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):
        context = []

        try:
            groups = request.user.groups.all()
            for group in groups:
                team = Group.objects.get(id=group.id)
                for user in team.user_set.all():
                    context.append({
                        "team": {
                            "id": int(team.id),
                            "name": team.name,
                            "users": {"id": int(user.id), "name": user.username},
                        }
                    })
        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return self.render_to_response(context, status=500)

        return self.render_to_response(context)


class AddUserTeamView(LoginRequiredMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):

        group_id = request.POST.get("group")
        user_id = request.POST.get("user")

        context = {"msg": "ok"}

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
            groupsofuser = user.groups.all()
            for groupuser in groupsofuser:
                if groupuser.name == group.name:
                    context["msg"] = str(_("User already registered with this team"))
                    log.exception("{}{}".format(_("Conflict:"), context["msg"]))
                    return self.render_to_response(context, status=500)

            user.groups.add(group)
            user.save()

            item = "group: {}, user: {}".format(group, user)
            actionlog.log(request.user.username, "create", item)

            return self.render_to_response(context)

        except Exception as e:
            context["msg"] = str(_("Error adding user, check user team"))
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return self.render_to_response(context, status=500)


class DeleteUserTeamView(LoginRequiredMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):
        group_id = request.POST.get("group")
        user_id = request.POST.get("user")

        context = {"msg": "ok"}

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)

            user.groups.remove(group)
            user.save()

            item = "group: {}, user: {}".format(group, user)
            actionlog.log(request.user.username, "delete", item)

            return self.render_to_response(context)

        except Exception as e:
            context["msg"] = str(_("Error removing user, check user and team"))
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return self.render_to_response(context, status=500)


class ListUsersTeamsView(SuperUserMixin, FormView):
    template_name = "vault/users_teams.html"

    def get(self, request, *args, **kwargs):
        context = {}
        context["groups"] = []

        for index, group in enumerate(Group.objects.all()):

            context["groups"].append({"id": int(group.id), "name": group.name, "users": []})

            for user in group.user_set.all():
                context["groups"][index]["users"].append({"email": user.email})

        context = update_default_context(request, context)

        return self.render_to_response(context)


class OAuthBearerCallback(OAuthCallback):
    "Callback de OAuth2 usando header de bearer"

    def get_client(self, provider):
        return OAuth2BearerClient(provider)

    def get_login_redirect(self, provider, user, access, new=False):
        return reverse("main")

    def get_user_id(self, provider, info):
        identifier = None

        if hasattr(info, "get"):
            identifier = info.get("email")

        if identifier is not None:
            return identifier

        return super(OAuthBearerCallback, self).get_user_id(provider, info)

    def get_or_create_user(self, provider, access, info):
        "Vincula o usuário django logado à sua conta"
        username = info.get("username")

        if username is None:
            username = info.get("email")

        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create_user(username=username)
            self._save_user_info(user, info)

            return user

    def _save_user_info(self, user, info):
        if "email" in info:
            user.email = info["email"]

        if "name" in info:
            parts = info["name"].split(" ", 1)
            user.first_name = parts[0]
            user.last_name = (len(parts) > 1) and parts[1] or ""

        user.save()


class OAuthVaultCallback(OAuthBearerCallback):
    pass


class OAuthVaultRedirect(OAuthRedirect):

    def get_additional_parameters(self, provider):

        if provider.name == "facebook":
            # Request permission to see user's email
            return {"scope": "email"}

        if provider.name == "google":
            # Request permission to see user's profile and email
            perms = ["userinfo.email", "userinfo.profile"]
            scope = " ".join(["https://www.googleapis.com/auth/" + p for p in perms])
            return {"scope": scope}

        return super(OAuthVaultRedirect, self).get_additional_parameters(provider)


@login_required
def team_manager_view(request, project=None):
    context = {}
    groups = []

    for group in request.user.groups.all():
        groups.append({
            "id": group.id,
            "name": group.name,
            "users": User.objects.filter(groups__in=[group.id])
        })

    context["groups"] = groups

    return render(request, "vault/team_manager/index.html", context)


@login_required
def list_users_outside_a_group(request):
    group_id = request.GET.get("group")

    if group_id is None:
        return HttpResponse(status=400)

    users = User.objects.exclude(groups__in=[group_id]).order_by("username")
    content = []

    for user in users:
        content.append({"id": user.id, "name": user.username, "email": user.email})

    return HttpResponse(json.dumps(content), content_type="application/json")


@login_required
def main_page(request):
    project = request.session.get("project_name")

    if project:
        return HttpResponseRedirect(reverse("dashboard", kwargs={"project": project}))
    else:
        return HttpResponseRedirect(reverse("change_project"))
