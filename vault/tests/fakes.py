# -*- coding: utf-8 -*-

import random
import factory
from datetime import datetime, timedelta

from io import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.backends.db import SessionStore


class GroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Group
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: "Group #{}".format(n))


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: "User #{}".format(n))
    is_superuser = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


def fake_request(path='/', method='GET', user=True, extra={}):
    params = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'wsgi.input': StringIO()
    }
    params.update(extra)

    req = WSGIRequest(params)

    if user:
        req.user = UserFactory.create(groups=(GroupFactory(), GroupFactory()))
    else:
        req.user = AnonymousUser()

    req.build_absolute_uri = lambda x=None: '/'

    # for sessions middleware
    req.session = build_fake_session()

    # for messages middleware
    req._messages = default_storage(req)

    req.get_host = lambda x=None: 'localhost'

    return req


def build_fake_session():
    fake_session = SessionStore()
    fake_session['token_time'] = timedelta(minutes=15) + datetime.utcnow()
    fake_session['project_id'] = '1'
    fake_session['project_name'] = 'fake_project'
    fake_session['service_catalog'] = {
        'object_store': {'adminURL': 'https://fake.api.globoi.com/v1/AUTH_XPTO',
                         'publicURL': 'http://fake.s3.glbimg.com/v1/AUTH_XPTO',
                         'internalURL': 'http://fake.i.s3.glbimg.com/v1/AUTH_XPTO'},

        'identity': {'adminURL': 'http://identity/admin',
                     'publicURL': 'http://identity/public',
                     'internalURL': 'http://identity/internal'},

        'block_storage': {'adminURL': 'http://block_storage/XPTO',
                          'publicURL': 'http://block_storage/XPTO',
                          'internalURL': 'http://block_storage/XPTO'}
    }

    return fake_session
