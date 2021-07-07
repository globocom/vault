# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView

from keystoneclient import exceptions

from storage.utils import delete_swift_account, update_swift_account
from actionlogger.actionlogger import ActionLogger
from identity.keystone import Keystone
from identity.forms import UserForm, CreateUserForm, UpdateUserForm, ProjectForm, DeleteProjectConfirm

from vault.jsoninfo import JsonInfo
from vault import utils
from vault.models import GroupProjects
from vault.views import SuperUserMixin, JSONResponseMixin, LoginRequiredMixin, ProjectCheckMixin


log = logging.getLogger(__name__)
actionlog = ActionLogger()


class WithKeystoneMixin:
    def __init__(self, *args, **kwargs):
        self.keystone = None
        super(WithKeystoneMixin, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.keystone = Keystone(request)
        except exceptions.AuthorizationFailure:
            msg = _("Unable to retrieve Keystone data")
            messages.add_message(request, messages.ERROR, msg)
            log.error(f"{request.user}: {msg}")

            # Redirects user back to previous page
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

        if self.keystone.conn is None:
            msg = _("Authorization error")
            messages.add_message(request, messages.ERROR, msg)
            log.error("Keystone: {}".format(msg))

        return super(WithKeystoneMixin, self).dispatch(request, *args, **kwargs)


class ListUserView(SuperUserMixin, WithKeystoneMixin, ProjectCheckMixin, TemplateView):
    template_name = "identity/users.html"

    def get_context_data(self, **kwargs):
        context = super(ListUserView, self).get_context_data(**kwargs)
        page = self.request.GET.get("page", 1)

        users = []

        try:
            users = self.keystone.user_list()
        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            messages.add_message(self.request, messages.ERROR, _("Unable to list users"))

        sorted_users = sorted(users, key=lambda l: l.name.lower())
        context["users"] = utils.generic_pagination(sorted_users, page)

        return context


class BaseUserView(SuperUserMixin, WithKeystoneMixin, FormView):
    form_class = UserForm

    def _fill_project_choices(self, form):
        if self.keystone and "project" in form.fields:
            items = [("", "---")]

            for i in self.keystone.project_list():
                if getattr(i, "enabled", None):
                    items.append((i.id, i.name))

            form.fields["project"].choices = items

    def _fill_role_choices(self, form):
        if self.keystone and "role" in form.fields:
            items = [("", "---")]

            for i in self.keystone.role_list():
                items.append((i.id, i.name))

            index = [items.index(item) for item in items if "_member_" in item]

            if index:
                items.pop(index[0])

            form.fields["role"].choices = items

    @method_decorator(sensitive_post_parameters("password", "password_confirm"))
    def dispatch(self, request, *args, **kwargs):
        project_name = request.session.get("project_name")
        self.success_url = reverse_lazy("admin_list_users", kwargs={"project": project_name})
        return super(BaseUserView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)

        self._fill_project_choices(form)
        self._fill_role_choices(form)

        return self.render_to_response(self.get_context_data(form=form, **kwargs))

    def get_context_data(self, **kwargs):
        context = super(BaseUserView, self).get_context_data(**kwargs)
        user_id = kwargs.get("user_id")
        form = kwargs.get("form")

        if not user_id:
            user_id = form.data.get("id")

        if user_id:
            user = self.keystone.user_get(user_id)
            form.initial = user.to_dict()
            form.fields["project"].initial = user.default_project_id
            context["user_id"] = user_id

        return context


class CreateUserView(BaseUserView):
    form_class = CreateUserForm
    template_name = "identity/user_create.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)

        self._fill_project_choices(form)
        self._fill_role_choices(form)

        if form.is_valid():
            post = request.POST

            enabled = False if post.get("enabled") in ("False", "0") else True

            try:
                user = self.keystone.user_create(
                    name=post.get("name"),
                    email=post.get("email"),
                    password=post.get("password"),
                    project_id=post.get("project"),
                    enabled=enabled,
                    domain=post.get("domain"),
                    role_id=post.get("role"),
                )

                messages.add_message(request, messages.SUCCESS, _("Successfully created user"))
                actionlog.log(request.user.username, "create", user)

            except Exception as e:
                log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
                messages.add_message(request, messages.ERROR, _("Error when creating user"))

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UpdateUserView(BaseUserView):
    form_class = UpdateUserForm
    template_name = "identity/user_edit.html"

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)

        self._fill_project_choices(form)

        if form.is_valid():
            post = request.POST
            enabled = False if post.get("enabled") in ("False", "0") else True

            try:
                user = self.keystone.user_get(post.get("id"))

                # can't modify primary project
                project = self.keystone.project_get(user.default_project_id)

                self.keystone.user_update(
                    user,
                    name=post.get("name"),
                    email=post.get("email"),
                    password=post.get("password"),
                    project=project.id,
                    enabled=enabled,
                    domain=post.get("domain"),
                )

                messages.add_message(request, messages.SUCCESS, _("Successfully updated user"))
                actionlog.log(request.user.username, "update", user)

            except Exception as e:
                log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
                messages.add_message(request, messages.ERROR, _("Error when updating user"))

        context = self.get_context_data(form=form, request=request)
        return self.render_to_response(context)


class DeleteUserView(BaseUserView):
    def get(self, request, *args, **kwargs):
        try:
            self.keystone.user_delete(kwargs.get("user_id"))
            messages.add_message(request, messages.SUCCESS, _("Successfully deleted user"))
            actionlog.log(request.user.username, "delete", "user_id: {}".format(kwargs.get("user_id")))

        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            messages.add_message(request, messages.ERROR, _("Error when deleting user"))

        project_name = request.session.get("project_name")
        success_url = reverse("admin_list_users", kwargs={"project": project_name})

        return HttpResponseRedirect(success_url)


class BaseProjectView(LoginRequiredMixin, WithKeystoneMixin, FormView):
    success_url = reverse_lazy("change_project")

    def get(self, request, *args, **kwargs):

        # edit_project is the non admin project update view
        if request.resolver_match is not None and request.resolver_match.url_name == "edit_project":

            project = self.keystone.project_get(kwargs.get("project_id"))

            form = ProjectForm(initial={"user": request.user, "action": "update"})
        else:
            form = ProjectForm(initial={"user": request.user})

        # Show only user groups
        form.fields["group"].queryset = request.user.groups

        context = self.get_context_data(form=form, request=request, **kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):

        request = kwargs.get("request")
        context = super(BaseProjectView, self).get_context_data(**kwargs)
        form = kwargs.get("form")

        project_id = kwargs.get("project_id")
        if not project_id:
            project_id = form.data.get("id")

        # Show role manager when superuser
        context["show_roles"] = request.user.is_superuser

        if project_id:
            project = self.keystone.project_get(project_id).to_dict()
            form.initial = project
            context["project"] = project
            context["identity_project_id"] = project_id
            context["has_id"] = True

            try:
                form.initial["group"] = GroupProjects.objects.get(project=project_id, owner=1).group_id
            except GroupProjects.DoesNotExist:
                form.initial["group"] = None

            if project.get("team_owner_id") is not None:
                try:
                    context["project"]["team"] = Group.objects.get(id=project["team_owner_id"])
                except Group.DoesNotExist:
                    context["project"]["team"] = None

            if project.get("first_team_id") is not None:
                try:
                    context["project"]["first_team"] = Group.objects.get(id=project["first_team_id"])
                except Group.DoesNotExist:
                    context["project"]["first_team"] = None

            user = self.keystone.find_user_with_u_prefix(project_id, "u")
            if user:
                context["user_project"] = user.name

            if context["show_roles"]:
                try:
                    users = self.keystone.user_list()
                    context["users"] = sorted(users, key=lambda l: l.name.lower())

                    roles = self.keystone.role_list()
                    context["roles"] = sorted(roles, key=lambda l: l.name.lower())
                except Exception as e:
                    log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))

        return context


class ListProjectView(SuperUserMixin, WithKeystoneMixin, ProjectCheckMixin, TemplateView):
    template_name = "identity/projects.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ListProjectView, self).get_context_data(**kwargs)
        page = self.request.GET.get("page", 1)

        context["projects"] = utils.generic_pagination(self._get_data(), page)

        return context

    def _get_data(self):
        """Retrieve sorted list of projects"""
        projects = []
        try:
            projects = [p.to_dict() for p in self.keystone.project_list()]
            projects = sorted(projects, key=lambda l: l["name"].lower())

            for prj in projects:
                prj["team"] = ""
                if prj.get("team_owner_id") is not None:
                    prj["team"] = Group.objects.filter(id=prj["team_owner_id"]).first()
        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            messages.add_message(self.request, messages.ERROR, _("Unable to list projects"))

        return projects


class CreateProjectSuccessView(LoginRequiredMixin, TemplateView):
    template_name = "identity/project_create_success.html"

    @method_decorator(utils.project_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request=request, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CreateProjectSuccessView, self).get_context_data(**kwargs)

        request = kwargs.get("request")

        context["project_info"] = request.session.get("project_info")
        context["project_info"]["auth_url"] = settings.KEYSTONE_URL

        project_name = context["project_info"]["project_name"]
        user_name = context["project_info"]["user_name"]
        password = context["project_info"]["user_password"]

        try:
            keystone = Keystone(request, username=user_name, password=password, project_name=project_name)
            context["project_info"]["endpoints"] = keystone.get_endpoints()
        except exceptions.AuthorizationFailure:
            msg = _("Unable to retrieve Keystone data")
            messages.add_message(request, messages.ERROR, msg)
            log.error(f"{request.user}: {msg}")

        return context


class CreateProjectView(BaseProjectView):
    template_name = "identity/project_create.html"
    form_class = ProjectForm
    success_url = reverse_lazy("change_project")

    def post(self, request, *args, **kwargs):
        form = ProjectForm(initial={"user": request.user}, data=request.POST)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form, request=request))

        group_id = request.POST.get("group")
        response = self.keystone.vault_project_create(
            request.POST.get("name"),
            group_id,
            description=request.POST.get("description"),
            first_team_id=group_id,
            team_owner_id=group_id,
            created_by="vault",
        )

        # Houve falha no cadastro
        if not response.get("status"):
            log.exception("Exception: {}".format(response.get("status")))

            messages.add_message(request, messages.ERROR, response.get("reason"))

            return self.render_to_response(self.get_context_data(form=form, request=request))

        # swift-cloud middleware
        if settings.SWIFT_CLOUD_ENABLED:
            cloud = request.POST.get("cloud")
            if cloud != "":
                endpoints = self.keystone.get_endpoints()
                storage_url = endpoints.get("object_store").get("adminURL")
                update_swift_account({"X-Account-Meta-Cloud": cloud}, storage_url, self.keystone.conn.auth_token)

        project = response.get("project")
        user = response.get("user")

        actionlog.log(request.user.username, "create", project)
        actionlog.log(request.user.username, "create", user)

        request.session["project_info"] = {
            "user_name": user.name,
            "project_name": project.name,
            "user_password": response.get("password"),
        }

        return redirect("create_project_success", project=project.name)


class ChangeProjectView(LoginRequiredMixin, WithKeystoneMixin, TemplateView):
    template_name = "identity/project_change.html"

    def get(self, request, *args, **kwargs):

        if self.request.user.groups.count() == 0:
            self.template_name = "identity/project_change_noteam.html"

        context = self.get_context_data(request=request, **kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ChangeProjectView, self).get_context_data(**kwargs)
        page = self.request.GET.get("page", 1)

        context["projects"] = utils.generic_pagination(self._get_data(), page)

        return context

    def _get_data(self):
        """Retrieve sorted list of projects"""
        user = self.request.user
        groups = user.groups.all()
        try:
            keystone = Keystone(self.request)
        except exceptions.AuthorizationFailure:
            msg = _("Unable to retrieve Keystone data")
            messages.add_message(self.request, messages.ERROR, msg)
            log.error(f"{self.request.user}: {msg}")

            return []

        projects = []

        for group in groups:
            gps = GroupProjects.objects.filter(group=group.id)
            gps_ks = [x for x in filter(lambda x: x.enabled, keystone.project_list())]

            for gp in gps:
                for gp_ks in gps_ks:
                    if gp.project == gp_ks.id and gp_ks not in projects:
                        projects.append(gp_ks)
                        break

            projects.sort(key=lambda x: x.name.lower())

        return projects


class UpdateProjectView(BaseProjectView):
    template_name = "identity/project_edit.html"

    def post(self, request, *args, **kwargs):
        post = request.POST
        project = self.keystone.project_get(post.get("id"))

        form = ProjectForm(data=post, initial={"user": request.user})

        if form.is_valid():
            enabled = True
            if post.get("enabled") in ["False", "0"]:
                enabled = False

            group_id = post.get("group")

            description = post.get("description")
            if description == "":
                description = None

            try:
                response = self.keystone.vault_project_update(
                    project.id, project.name, group_id, description=description, enabled=enabled, team_owner_id=group_id
                )

                if response["status"]:
                    messages.add_message(request, messages.SUCCESS, _("Successfully updated project"))
                else:
                    messages.add_message(request, messages.ERROR, _(response["reason"]))

                actionlog.log(request.user.username, "update", project)
            except Exception as e:
                log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
                messages.add_message(request, messages.ERROR, _("Error when updating project"))

        context = self.get_context_data(form=form, request=request)
        return self.render_to_response(context)


class DeleteProjectView(BaseProjectView):
    template_name = "identity/project_delete_confirm.html"

    def get(self, request, *args, **kwargs):
        form = DeleteProjectConfirm()
        return self.render_to_response(self.get_context_data(form=form, request=request))

    def post(self, request, *args, **kwargs):
        form = DeleteProjectConfirm(data=request.POST)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form, request=request))

        user = form.data.get("user")
        password = form.data.get("password")

        project_id = self.kwargs.get("project_id")
        project_name = self.keystone.project_get(project_id).name

        try:
            keystone_app = Keystone(request, username=user, password=password, project_name=project_name)
        except exceptions.Unauthorized:
            # Fail to authenticate with sent credentials
            messages.add_message(request, messages.ERROR, _("Invalid credentials."))

            return self.render_to_response(context=self.get_context_data(form=form, request=request))
        except exceptions.AuthorizationFailure:
            msg = _("Unable to retrieve Keystone data")
            messages.add_message(request, messages.ERROR, msg)
            log.error(f"{request.user}: {msg}")

            return self.render_to_response(context=self.get_context_data(form=form, request=request))

        endpoints = keystone_app.get_endpoints()
        storage_url = endpoints.get("object_store").get("adminURL")
        auth_token = self.keystone.conn.auth_token

        swift_del_result = delete_swift_account(storage_url, auth_token)

        if not swift_del_result:
            messages.add_message(request, messages.ERROR, _("Error when deleting swift account"))

            return HttpResponseRedirect(
                reverse("edit_project", kwargs={"project_id": project_id, "project": project_name})
            )

        try:
            self.keystone.vault_project_delete(project_name)
            messages.add_message(request, messages.SUCCESS, _("Successfully deleted project."))

        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            messages.add_message(request, messages.ERROR, _("Error when deleting project"))

        # Purge project from current projects
        utils.purge_current_project(request, project_id)

        project_name = request.session.get("project_name")
        success_url = reverse("change_project")

        return HttpResponseRedirect(success_url)


class ListUserRoleView(SuperUserMixin, WithKeystoneMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):
        project_id = request.POST.get("project")
        context = {}

        if not project_id:
            return self.render_to_response(context)

        try:
            project_users = self.keystone.user_list(project_id=project_id)

            context["users"] = []
            unique_users = set()

            for user in project_users:
                if user.name not in unique_users:
                    unique_users.add(user.name)
                    context["users"].append(
                        {"id": user.id, "username": user.name, "roles": self.get_user_roles(user, project_id)}
                    )

            # sorting users by username
            context["users"] = [x for x in sorted(context["users"], key=lambda x: x.get("username"))]

            return self.render_to_response(context)

        except Exception as e:
            context["msg"] = "Error listing users"
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))

            return self.render_to_response(context, status=500)

    def get_user_roles(self, user, project_id):
        return [{"id": r.id, "name": r.name} for r in self.keystone.list_user_roles(user, project_id)]


class AddUserRoleView(SuperUserMixin, WithKeystoneMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):
        project = request.POST.get("project")
        role = request.POST.get("role")
        user = request.POST.get("user")

        context = {"msg": "ok"}

        try:
            self.keystone.add_user_role(project=project, role=role, user=user)

            item = "project: {}, role: {}, user: {}".format(project, role, user)
            actionlog.log(request.user.username, "create", item)

            return self.render_to_response(context)

        except exceptions.Conflict as e:
            context["msg"] = str(_("User already registered with this role"))
            log.exception("{}{}".format(_("Conflict:"), e))
            return self.render_to_response(context, status=500)

        except Exception as e:
            context["msg"] = str(_("Error adding user"))
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return self.render_to_response(context, status=500)


class DeleteUserRoleView(SuperUserMixin, WithKeystoneMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):
        project = request.POST.get("project")
        role = request.POST.get("role")
        user = request.POST.get("user")

        context = {"msg": "ok"}

        try:
            self.keystone.remove_user_role(project=project, role=role, user=user)

            item = "project: {}, role: {}, user: {}".format(project, role, user)
            actionlog.log(request.user.username, "delete", item)

            return self.render_to_response(context)

        except Exception as e:
            context["msg"] = str(_("Error removing user"))
            log.exception("Exception: {}".format(e))
            return self.render_to_response(context, status=500)


class UpdateProjectUserPasswordView(LoginRequiredMixin, WithKeystoneMixin, View, JSONResponseMixin):
    def post(self, request, *args, **kwargs):
        project_id = request.POST.get("project")
        context, status = {}, 200

        try:
            user = self.keystone.find_user_with_u_prefix(project_id, "u")
            new_password = Keystone.create_password()

            self.keystone.user_update(user, password=new_password)
            context = {"new_password": new_password}
            actionlog.log(request.user.username, "update", user)

        except Exception as e:
            context = {"msg": str(_("Error updating password"))}
            log.exception("Exception: {}".format(e))
            status = 500

        return self.render_to_response(context, status=status)


class KeystoneJsonInfo(JsonInfo, WithKeystoneMixin):
    def __init__(self, *args, **kwargs):
        self.keystone = kwargs["keystone"]
        super(KeystoneJsonInfo, self).__init__(*args, **kwargs)

    def generate_menu_info(self):
        project_name = self.request.session.get("project_name")
        return {
            "name": str(_("Identity")),
            "icon": "fas fa-key",
            "url": reverse("projects", kwargs={"project": project_name}),
            "subitems": [
                {"name": str(_("Projects")), "icon": "", "url": reverse("projects", kwargs={"project": project_name})},
                {
                    "name": str(_("Users")),
                    "icon": "",
                    "url": reverse("admin_list_users", kwargs={"project": project_name}),
                },
            ],
        }

    def generate_widget_info(self):
        project_name = self.request.session.get("project_name")

        try:
            users = self.keystone.user_list()
        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return {"error": "Unable to list users"}
        try:
            projects = self.keystone.project_list()
        except Exception as e:
            log.exception("{}{}".format(_("Exception:").encode("UTF-8"), e))
            return {"error": "Unable to list projects"}

        return [
            {
                "type": "default",
                "name": "keystone",
                "title": str(_("Keystone")),
                "subtitle": str(_("Identity")),
                "color": "green",
                "icon": "fas fa-key",
                "url": reverse("projects", kwargs={"project": project_name}),
                "properties": [
                    {"name": str(_("projects")), "description": "", "value": len(projects)},
                    {"name": str(_("users")), "description": "", "value": len(users)},
                ],
                "buttons": [
                    {"name": str(_("Projects")), "url": reverse("projects", kwargs={"project": project_name})},
                    {"name": str(_("Users")), "url": reverse("admin_list_users", kwargs={"project": project_name})},
                ],
            }
        ]


class JsonInfoView(SuperUserMixin, ProjectCheckMixin, WithKeystoneMixin, View):
    def get(self, request, *args, **kwargs):
        ksinfo = KeystoneJsonInfo(keystone=self.keystone, request=request)

        return ksinfo.render(request)
