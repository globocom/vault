# -*- coding:utf-8 -*-

from StringIO import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.backends.db import SessionStore


def fake_request(path='/', method='GET', user=None, extra={}):
    params = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'wsgi.input': StringIO()
    }
    params.update(extra)

    req = WSGIRequest(params)
    req.user = user or AnonymousUser()
    req.user.project_id = 1

    req.build_absolute_uri = lambda x=None: '/'

    # for sessions middleware
    req.session = SessionStore()
    req.session['project_id'] = 1

    # for messages middleware
    req._messages = default_storage(req)

    return req
