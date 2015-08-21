# -*- coding:utf-8 -*-

import factory

from StringIO import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User, Group
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.backends.db import SessionStore


# factories.py
class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        strategy = factory.BUILD_STRATEGY

    name = factory.Sequence(lambda n: "Group #%s" % n)


# TODO: Carregando grupos reais do banco; corrigir para carregar GroupFactory
class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
        strategy = factory.BUILD_STRATEGY

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


def fake_request(path='/', method='GET', user=None, extra={}):
    params = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'wsgi.input': StringIO()
    }
    params.update(extra)

    req = WSGIRequest(params)
    # req.user = user or AnonymousUser()
    req.user = user or UserFactory(groups=[GroupFactory()])
    req.user.project_id = 1

    req.build_absolute_uri = lambda x=None: '/'

    # for sessions middleware
    req.session = SessionStore()
    req.session['project_id'] = 1

    # for messages middleware
    req._messages = default_storage(req)

    return req
