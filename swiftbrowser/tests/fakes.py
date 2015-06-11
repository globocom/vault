# -*- coding:utf-8 -*-

import StringIO

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import InMemoryUploadedFile


# From: http://www.rkblog.rk.edu.pl/w/p/temporary-files-django-tests-and-fly-file-manipulation/
def get_temporary_text_file():
    io = StringIO.StringIO()
    io.write('foo')
    text_file = InMemoryUploadedFile(io, None, 'foo.txt', 'text', io.len, None)
    text_file.seek(0)
    return text_file


def get_account():
    account_stat = {
        'content-length': '147',
        'x-account-object-count': '5',
        'server': 'nginx',
        'connection': 'keep-alive',
        'x-timestamp': '1405090896.54396',
        'x-account-meta-temp-url-key': 'ipytkrl2sij2gbycz10xrem23hfsz3z4',
        'x-trans-id': 'tx11e34a0efd904a7cbd6e7-0053f49d36',
        'date': 'Wed, 20 Aug 2014 13:05:58 GMT',
        'x-account-bytes-used': '46',
        'x-account-container-count': '3',
        'content-type': 'application/json; charset=utf-8',
        'accept-ranges': 'bytes'
    }

    containers = [
        {'count': 4, 'bytes': 32, 'name': 'container1'},
        {'count': 0, 'bytes': 0, 'name': 'container2'},
        {'count': 1, 'bytes': 14, 'name': 'container3'}
    ]

    return (account_stat, containers)


def get_container():
    objects = [
        {
            'bytes': 8,
            'last_modified': '2014-07-11T18:51:45.260310',
            'name': 'obj_pelo_vip.html',
            'content_type': 'text/html'
        },
        {
            'bytes': 8,
            'last_modified': '2014-07-11T17:01:35.526450',
            'hash': 'bdf0a1cfded326aeb439fa86bd3427ab',
            'name': 'ok',
            'content_type': 'application/octet-stream'
        },
        {
            'bytes': 0,
            'last_modified': '2014-07-11T17:01:35.526450',
            'hash': 'bdf0a1cfded326aeb439fa86bd3427ab',
            'name': 'pseudofolder/',
            'content_type': 'application/directory'
        }
    ]

    return ({}, objects)


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


class FakeUser(AnonymousUser):
    """ Fake Keystone Resource (e.g. User, Project, Role) """

    def __init__(self, n=0, name=None):
        super(FakeUser, self).__init__()

        self.id = n
        self.username = name if name else "FakeUser%d" % n
        self.enabled = True
        self.description = ''
        self.project_id = 1
        self.token = FakeToken()
        self.service_catalog = [
            {
                u'endpoints': [{
                    u'adminURL': u'https://fakeurl',
                    u'region': u'RegionOne',
                    u'id': u'fakeid',
                    u'internalURL': u'https://fakeurl',
                    u'publicURL': u'http://fakepublicurl'
                }],
                u'endpoints_links': [],
                u'type': u'object-store',
                u'name': u'swift'
            },
            {
                u'endpoints': [{
                    u'adminURL': u'https://fakeurl',
                    u'region': u'RegionOne',
                    u'id': u'fakeid',
                    u'internalURL': u'https://fakeurl',
                    u'publicURL': u'https://fakeurl',
                }],
                u'endpoints_links': [],
                u'type': u'identity',
                u'name': u'keystone'
            }
        ]


class FakeRequestResponse(object):

    def __init__(self, status_code=200, content=None, headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = headers
