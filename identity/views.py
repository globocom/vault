# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView

from django.views.decorators.debug import sensitive_post_parameters

from keystoneclient.exceptions import Conflict

from swiftbrowser.utils import delete_swift_account

from actionlogger import ActionLogger
from identity.keystone import Keystone
from identity.forms import (UserForm, CreateUserForm, UpdateUserForm,
                            ProjectForm, DeleteProjectConfirm)

from vault import utils
from vault.models import GroupProjects, AreaProjects
from vault.views import SuperUserMixin, JSONResponseMixin, LoginRequiredMixin

log = logging.getLogger(__name__)
actionlog = ActionLogger()


class ListUserView(SuperUserMixin, TemplateView):
    template_name = "identity/users.html"

    def get_context_data(self, **kwargs):
        context = super(ListUserView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)

        users = []

        try:
            users = self.keystone.user_list()
        except Exception as e:
            log.exception('Exception: %s' % e)
            messages.add_message(self.request, messages.ERROR,
                                 "Unable to list users")

        sorted_users = sorted(users, key=lambda l: l.name.lower())
        context['users'] = utils.generic_pagination(sorted_users, page)

        return context


class BaseUserView(SuperUserMixin, FormView):
    form_class = UserForm
    success_url = reverse_lazy('admin_list_users')

    def _fill_project_choices(self, form):
        if self.keystone and 'project' in form.fields:
            items = [('', '---')]

            for i in self.keystone.project_list():
                if getattr(i, 'enabled', None):
                    items.append((i.id, i.name))

            form.fields['project'].choices = items

    def _fill_role_choices(self, form):
        if self.keystone and 'role' in form.fields:
            items = [('', '---')]

            for i in self.keystone.role_list():
                items.append((i.id, i.name))

            form.fields['role'].choices = items

    @method_decorator(sensitive_post_parameters('password', 'password_confirm'))
    def dispatch(self, *args, **kwargs):
        return super(BaseUserView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)

        self._fill_project_choices(form)
        self._fill_role_choices(form)

        return self.render_to_response(
            self.get_context_data(form=form, **kwargs)
        )

    def get_context_data(self, **kwargs):
        context = super(BaseUserView, self).get_context_data(**kwargs)
        user_id = kwargs.get('user_id')
        form = kwargs.get('form')

        if not user_id:
            user_id = form.data.get('id')

        if user_id:
            user = self.keystone.user_get(user_id)
            form.initial = user.to_dict()
            form.fields['project'].initial = user.project_id
            context['user_id'] = user_id

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

            enabled = False if post.get('enabled') in ('False', '0') else True

            try:
                user = self.keystone.user_create(name=post.get('name'),
                    email=post.get('email'), password=post.get('password'),
                    project_id=post.get('project'), enabled=enabled,
                    domain=post.get('domain'), role_id=post.get('role'))

                messages.add_message(request, messages.SUCCESS,
                                     'Successfully created user')
                actionlog.log(request.user.username, 'create', user)

            except Exception as e:
                log.exception('Exception: %s' % e)
                messages.add_message(request, messages.ERROR,
                                     'Error when create user')

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
            enabled = False if post.get('enabled') in ('False', '0') else True

            try:
                user = self.keystone.user_get(post.get('id'))

                # can't modify primary project
                project = self.keystone.project_get(user.project_id)

                self.keystone.user_update(user, name=post.get('name'),
                    email=post.get('email'), password=post.get('password'),
                    project=project, enabled=enabled, domain=post.get('domain'))

                messages.add_message(request, messages.SUCCESS,
                                     'Successfully updated user')
                actionlog.log(request.user.username, 'update', user)

            except Exception as e:
                log.exception('Exception: %s' % e)
                messages.add_message(request, messages.ERROR,
                                     'Error when update user')

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DeleteUserView(BaseUserView):

    def get(self, request, *args, **kwargs):

        try:
            self.keystone.user_delete(kwargs.get('user_id'))
            messages.add_message(request, messages.SUCCESS,
                                 'Successfully deleted user')
            actionlog.log(request.user.username, 'delete',
                          'user_id: %s' % kwargs.get('user_id'))

        except Exception as e:
            log.exception('Exception: %s' % e)
            messages.add_message(request, messages.ERROR,
                                 'Error when delete user')

        return HttpResponseRedirect(self.success_url)


class BaseProjectView(LoginRequiredMixin, FormView):
    success_url = reverse_lazy('dashboard')

    def get(self, request, *args, **kwargs):
        if request.resolver_match is not None and request.resolver_match.url_name == 'edit_project':
            form = ProjectForm(initial={'user': request.user, 'action': 'update'})
        else:
            form = ProjectForm(initial={'user': request.user})

        context = self.get_context_data(form=form, request=request, **kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):

        request = kwargs.get('request')
        context = super(BaseProjectView, self).get_context_data(**kwargs)
        project_id = kwargs.get('project_id')
        form = kwargs.get('form')

        # Mostra a gerencia de roles qd for superuser acessando admin
        context['show_roles'] = request.user.is_superuser and \
                                request.path[0:15] == '/admin/project/'

        if not project_id:
            project_id = form.data.get('id')

        if project_id:
            project = self.keystone.project_get(project_id)
            form.initial = project.to_dict()

            group_project = GroupProjects.objects.get(project_id=project_id)
            area_project = AreaProjects.objects.get(project_id=project_id)

            form.initial['groups'] = group_project.group_id
            form.initial['areas'] = area_project.area_id

            context['idendity_project_id'] = project_id
            context['has_id'] = True

            user = self.keystone.return_find_u_user(kwargs.get('project_id'))

            if user:
                context['user_project'] = user.username

            if context['show_roles']:

                try:
                    users = self.keystone.user_list()
                    context['users'] = sorted(users, key=lambda l: l.name.lower())

                    roles = self.keystone.role_list()
                    context['roles'] = sorted(roles, key=lambda l: l.name.lower())
                except Exception as e:
                    log.exception('Exception: %s' % e)

        return context


class ListProjectView(SuperUserMixin, TemplateView):
    template_name = "identity/projects.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ListProjectView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)

        context['is_admin'] = self.request.path[0:16] == '/admin/projects/'

        try:
            projects = sorted(self.keystone.project_list(),
                                key=lambda l: l.name.lower())
            context['projects'] = utils.generic_pagination(projects, page)
        except Exception as e:
            log.exception('Exception: %s' % e)
            messages.add_message(self.request, messages.ERROR,
                                 "Unable to list projects")

        return context


class CreateProjectSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'identity/project_create_success.html'

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(request=request, **kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CreateProjectSuccessView, self).get_context_data(**kwargs)

        request = kwargs.get('request')

        context['project_info'] = request.session.get('project_info')
        context['project_info']['auth_url'] = settings.KEYSTONE_URL

        project_name = context['project_info']['project_name']
        user_name = context['project_info']['user_name']
        password = context['project_info']['user_password']

        keystone = Keystone(request, username=user_name, password=password,
                            tenant_name=project_name)

        context['project_info']['endpoints'] = keystone.get_endpoints()

        return context


class CreateProjectView(BaseProjectView):
    template_name = "identity/project_create.html"
    form_class = ProjectForm
    success_url = reverse_lazy('projects')

    def post(self, request, *args, **kwargs):
        form = ProjectForm(initial={'user': request.user}, data=request.POST)

        if form.is_valid():
            post = request.POST
            description = post.get('description')

            if description == '':
                description = None

            response = self.keystone.vault_create_project(post.get('name'),
                                                 post.get('groups'),
                                                 post.get('areas'),
                                                 description=description)

            # Houve falha no cadastro
            if not response.get('status'):
                log.exception('Exception: {}'.format(response.get('status')))
                messages.add_message(request, messages.ERROR,
                                     response.get('reason'))

                return self.render_to_response(self.get_context_data(form=form, request=request))

            project = response.get('project')
            user = response.get('user')

            actionlog.log(request.user.username, 'create', project)
            actionlog.log(request.user.username, 'create', user)

            request.session['project_info'] = {
                'user_name': user.name,
                'project_name': project.name,
                'user_password': response.get('password')
            }

            return redirect('create_project_success')
        else:
            return self.render_to_response(self.get_context_data(form=form, request=request))


class UpdateProjectView(BaseProjectView):
    template_name = "identity/project_edit.html"

    def post(self, request, *args, **kwargs):

        form = ProjectForm(initial={'user': request.user}, data=request.POST)

        post = request.POST

        if form.is_valid():
            enabled = False if post.get('enabled') in ('False', '0') else True
            group_id = post.get('groups')
            area_id = post.get('areas')
            description = post.get('description')

            if description == '':
                description = None

            try:
                project = self.keystone.project_get(post.get('id'))

                self.keystone.vault_update_project(project.id, project.name,
                                              group_id, area_id,
                                              description=description,
                                              enabled=enabled)

                messages.add_message(request, messages.SUCCESS,
                                     'Successfully updated project')

                actionlog.log(request.user.username, 'update', project)

            except Exception as e:
                log.exception('Exception: %s' % e)
                messages.add_message(request, messages.ERROR,
                                     "Error when update project")

            return self.form_valid(form)
        else:
            context = self.get_context_data(form=form, request=request)
            return self.render_to_response(context)


class DeleteProjectView(BaseProjectView):
    template_name = "identity/project_delete_confirm.html"

    def get(self, request, *args, **kwargs):
        form = DeleteProjectConfirm()
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):

        post = request.POST
        user = post.get('user')
        password = post.get('password')

        project_id = self.kwargs.get('project_id')
        project_name = self.keystone.project_get(project_id).name
        keystone_app = Keystone(request, username=user, password=password,
                                tenant_name=project_name)

        if not keystone_app.conn:
            # Falhou ao auntenticar com as credenciais enviadas pelo usuario
            messages.add_message(request, messages.ERROR,
                                 'User or password are incorrect')
            form = DeleteProjectConfirm(data=request.POST)

            context = self.get_context_data(form=form, request=request)
            return self.render_to_response(context)

        endpoints = keystone_app.get_endpoints()

        storage_url = endpoints['adminURL']
        auth_token = self.keystone.conn.auth_token

        swift_del_result = delete_swift_account(storage_url, auth_token)

        if not swift_del_result:
            messages.add_message(request, messages.ERROR,
                                 'Error when delete project')

            return HttpResponseRedirect(reverse('edit_project', kwargs={'project_id': project_id}))

        try:
            self.keystone.vault_delete_project(project_id)
            messages.add_message(request, messages.SUCCESS, 'Successfully deleted project')

        except Exception as e:
            log.exception('Exception: %s' % e)
            messages.add_message(request, messages.ERROR,
                                 'Error when delete project')

        return HttpResponseRedirect(self.success_url)


class ListUserRoleView(SuperUserMixin, View, JSONResponseMixin):

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get('project')
        context = {}

        try:
            project_users = self.keystone.user_list(project_id=project_id)

            context['users'] = []
            unique_users = set()

            for user in project_users:
                if user.username not in unique_users:
                    unique_users.add(user.username)
                    context['users'].append({
                        'id': user.id,
                        'username': user.username,
                        'roles': self.get_user_roles(user, project_id)
                    })

            return self.render_to_response(context)

        except Exception as e:
            context['msg'] = 'Error listing users'
            log.exception('Exception: %s' % e)

            return self.render_to_response(context, status=500)

    def get_user_roles(self, user, project_id):
        # TODO: in v3 client users won't list roles (verify role_assignments)
        return [{'id': r.id, 'name': r.name}
                for r in user.list_roles(project_id)]


class AddUserRoleView(SuperUserMixin, View, JSONResponseMixin):

    def post(self, request, *args, **kwargs):

        project = request.POST.get('project')
        role = request.POST.get('role')
        user = request.POST.get('user')

        context = {'msg': 'ok'}

        try:
            self.keystone.add_user_role(project=project, role=role, user=user)

            item = 'project: %s, role: %s, user: %s' % (project, role, user)
            actionlog.log(request.user.username, 'create', item)

            return self.render_to_response(context)

        except Conflict as e:
            context['msg'] = 'User already registered with this role'
            log.exception('Conflict: %s' % e)
            return self.render_to_response(context, status=500)

        except Exception as e:
            context['msg'] = 'Error adding user'
            log.exception('Exception: %s' % e)
            return self.render_to_response(context, status=500)


class DeleteUserRoleView(SuperUserMixin, View, JSONResponseMixin):

    def post(self, request, *args, **kwargs):

        project = request.POST.get('project')
        role = request.POST.get('role')
        user = request.POST.get('user')

        context = {'msg': 'ok'}

        try:
            self.keystone.remove_user_role(project=project, role=role, user=user)

            item = 'project: %s, role: %s, user: %s' % (project, role, user)
            actionlog.log(request.user.username, 'delete', item)

            return self.render_to_response(context)

        except Exception as e:
            context['msg'] = 'Error removing user'
            log.exception('Exception: %s' % e)
            return self.render_to_response(context, status=500)


class UpdateProjectUserPasswordView(LoginRequiredMixin, View, JSONResponseMixin):

    def get(self, request, *args, **kwargs):

        context = {}
        try:
            user = self.keystone.return_find_u_user(kwargs.get('project_id'))
            new_password = Keystone.create_password()

            self.keystone.user_update(user, password=new_password)
            context = {'new_password': new_password}

            actionlog.log(request.user.username, 'update', user)
        except Exception as e:
            log.exception('Exception: %s' % e)

        return self.render_to_response(context, status=200)
