# -*- coding: utf-8 -*-

import factory
from datetime import datetime

from django.contrib.auth.models import User, Group

from vault.models import GroupProjects


class FakeResource:
    """ Fake Keystone Resource (e.g. User, Project, Role) """
    def __init__(self, n=0, name=None):
        self.id = n
        self.name = name if name else "FakeResource{:d}".format(n)
        self.enabled = True
        self.description = ''
        self.project_id = 1

    def to_dict(self):
        return self.__dict__


class FakeToken:
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
class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ('name',)
        # strategy = factory.BUILD_STRATEGY

    # id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: "Group #{}".format(n))


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('first_name', 'last_name', 'is_superuser',)
        # strategy = factory.BUILD_STRATEGY

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


class GroupProjectsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = GroupProjects
        # strategy = factory.BUILD_STRATEGY
