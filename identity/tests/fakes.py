# -*- coding: utf-8 -*-

import factory
from django.contrib.auth.models import User, Group

from vault.models import Project, Area, GroupProjects, AreaProjects


class FakeResource(object):
    """ Fake Keystone Resource (e.g. User, Project, Role) """
    def __init__(self, n=0, name=None):
        self.id = n
        self.name = name if name else "FakeResource%d" % n
        self.enabled = True
        self.description = ''
        self.project_id = 1


class FakeToken(object):
    """ Fake Keystone Token """
    def __init__(self, id="faketokenid"):
        self.id = id


class FakeKeystone:

    def __init__(self, request):
        self.users = FakeResource(1)
        self.roles = FakeResource(1)
        self.tenants = FakeResource(1)
        self.projects = FakeResource(1)

        self.users.get = lambda a: request.user
        self.users.create = lambda name, password, email, project, enabled, domain=None: None
        self.users.update = lambda user, **kwargs: None
        self.roles.get = lambda id: FakeResource(id)
        self.tenants.get = lambda a: FakeResource(1)
        self.tenants.create = lambda name, domain_id='default', description=None, enabled=True: None
        self.projects.get = lambda a: FakeResource(1)


# factories.py
class GroupFactory(factory.Factory):
    class Meta:
        strategy = factory.BUILD_STRATEGY
        model = Group

    name = factory.Sequence(lambda n: "Group #%s" % n)


class UserFactory(factory.Factory):

    class Meta:
        strategy = factory.BUILD_STRATEGY
        model = User

    pk = 1
    first_name = "John"
    last_name = "Doe"
    is_superuser = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)


class ProjectFactory(factory.Factory):

    class Meta:
        strategy = factory.BUILD_STRATEGY
        model = Project


class AreaFactory(factory.Factory):

    class Meta:
        strategy = factory.BUILD_STRATEGY
        model = Area


class GroupProjectsFactory(factory.Factory):

    class Meta:
        strategy = factory.BUILD_STRATEGY
        model = GroupProjects


class AreaProjectsFactory(factory.Factory):

    class Meta:
        strategy = factory.BUILD_STRATEGY
        model = AreaProjects
