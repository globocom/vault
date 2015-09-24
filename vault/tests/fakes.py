# -*- coding: utf-8 -*-

import factory

from StringIO import StringIO
from mock import Mock

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User, Group, AnonymousUser
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

    req.user = user or AnonymousUser()
    req.user.id = ''
    req.user.username = 'user'
    req.user.first_name = 'mock_user'
    req.user.is_superuser = True
    req.user.groups.all = lambda: [GroupFactory(id=1)]

    req.build_absolute_uri = lambda x=None: '/'

    # for sessions middleware
    req.session = build_fake_session()

    # for messages middleware
    req._messages = default_storage(req)

    req.get_host = lambda x=None: 'localhost'

    return req


def build_fake_session():
    fake_session = SessionStore()
    fake_session['project_id'] = '1'
    fake_session['service_catalog'] = {
            'adminURL': 'https://fake.api.globoi.com/v1/AUTH_XPTO',
            'publicURL': 'http://fake.s3.glbimg.com/v1/AUTH_XPTO',
            'internalURL': 'http://fake.i.s3.glbimg.com/v1/AUTH_XPTO'
    }

    return fake_session
