# -*- coding:utf-8 -*-


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
        self.projects.get = lambda a: FakeResource(1)
