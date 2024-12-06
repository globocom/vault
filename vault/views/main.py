"""
Vault Generic Views
"""
import json
import logging

from django.contrib import messages
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth.views import LoginView
from django.contrib.auth.signals import user_logged_out
from django.conf import settings
from django.apps import apps

from keystoneclient import exceptions
from functools import wraps
from datetime import datetime

from authlib.integrations.django_client import OAuth

from actionlogger.actionlogger import ActionLogger
from identity.keystone import Keystone
from vault.utils import (update_default_context, save_current_project,
    set_current_project, maybe_update_token, project_required)
from vault.client import OAuth2BearerClient

log = logging.getLogger(__name__)
actionlog = ActionLogger()
oauth = OAuth()

oauth.register(
    name='oidc',
    client_id=settings.OIDC_CLIENT_ID,
    client_secret=settings.OIDC_CLIENT_SECRET,
    userinfo_endpoint=settings.OIDC_USERINFO_ENDPOINT,
    access_token_url=settings.OIDC_ACCESS_TOKEN_URL,
    access_token_params=None,
    authorize_url=settings.OIDC_AUTHORIZE_URL,
    authorize_params=None,
    client_kwargs={'scope': 'email'},
)


def user_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            expires_at = request.session.get('expires_at')
            expires_at_date = None
            if expires_at:
                expires_at_date = datetime.utcfromtimestamp(expires_at)
            if not expires_at_date or expires_at_date < datetime.utcnow():
                # log.info('Token has expired for user [{}]'.format(request.user))
                messages.add_message(request, messages.ERROR, "Seu token expirou")
                return redirect(settings.LOGIN_URL)
            if request.user:
                return view_func(request, *args, **kwargs)
            return redirect(settings.LOGIN_URL)
        return _wrapped_view
    return decorator

def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def logout(request):
    """
    Remove the authenticated user's ID from the request and flush their session
    data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, 'user', None)
    if not getattr(user, 'is_authenticated', True):
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)
    request.session.flush()
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

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

        providers.append({
            "name": settings.PROVIDER_NAME,
            "url": reverse("oidc-login")
        })

        context.update({
            "providers": providers,
            "username": user and user.get_username()
        })

        return context


class VaultLogout(View):

    def get(self, request):
        user = request.user
        logout(request)
        log.info(_("User logged out:") + " [{}]".format(user))
        url = f"{settings.OIDC_LOGOUT}?client_id={settings.OIDC_CLIENT_ID}&redirect_uri={settings.HTTP_PROTOCOL}://{request.get_host()}{settings.LOGIN_URL}"
        # return HttpResponseRedirect(reverse("main"))
        return redirect(url)


def handler500(request):
    response = render(request, "500.html", {})
    response.status_code = 500

    return response


class UpdateTeamsUsersView(LoginRequiredMixin, FormView):
    template_name = "vault/team_manager/users_teams.html"

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
    def get(self, request, *args, **kwargs):
        context = []

        try:
            groups = request.user.groups.all()
            for group in groups:
                team = Group.objects.get(id=group.id)
                context.append({
                    "id": int(team.id),
                    "name": team.name,
                    "users": [{
                        "id": int(user.id),
                        "name": user.username
                    } for user in team.user_set.all()]
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


class OIDCLogin(View):

    def get(self, request):
        oidc = oauth.create_client('oidc')
        redirect_uri = f"{settings.HTTP_PROTOCOL}://{request.get_host()}{settings.LOGIN_REDIRECT_URL}"
        return oidc.authorize_redirect(request, redirect_uri)


class OIDCAuthorize(View):

    def get(self, request):
        token = oauth.oidc.authorize_access_token(request)
        info = oauth.oidc.userinfo(token=token)
        info.is_authenticated = True
        user = self.get_or_create_user(info)
        request.user = user
        request._cached_user = user
        request.session['user'] = user
        request.session['_auth_user_id'] = user.id
        request.session['_auth_user_backend'] = user
        request.session['access_token'] = token.get('access_token')
        request.session['refresh_token'] = token.get('refresh_token')
        request.session['expires_at'] = token.get('expires_at')
        return redirect(reverse("change_project"))

    def get_or_create_user(self, info):
        "Vincula o usuário django logado à sua conta"
        username = info.get("username")

        if username is None:
            username = info.get("email")

        name = username.split('@')
        info['name'] = name[0]

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

    users = User.objects.exclude(
        groups__in=[group_id]).order_by("username")
    content = []

    for user in users:
        content.append({
            "id": user.id,
            "name": user.username,
            "email": user.email
        })

    return HttpResponse(
        json.dumps(content), content_type="application/json")


@login_required
def main_page(request):
    project = request.session.get("project_name")

    if project:
        return HttpResponseRedirect(
            reverse("dashboard", kwargs={"project": project}))
    else:
        return HttpResponseRedirect(reverse("change_project"))


@login_required
def apps_info(request):
    endpoints = []
    project_name = request.session.get('project_name')

    for conf in apps.get_app_configs():
        if hasattr(conf, 'vault_app'):
            endpoints.append(
                "/p/{}/{}/api/info".format(project_name, conf.name))

    return HttpResponse(
        json.dumps(endpoints), content_type="application/json")
