# -*- coding:utf-8 -*-

import syslog
from models import Audit


class ActionNotFound(Exception):
    pass


class ActionLogger(object):
    """ A wrapper to log actions """

    def __init__(self):
        self.audit = Audit()
        self._actions = {'create': 'Criou',
                         'update': 'Atualizou',
                         'delete': 'Removeu',
                         'upload': 'Realizou Upload',
                         'download': 'Realizou Download',
                         'enable': 'Habilitou',
                         'disable': 'Desabilitou'}

    def log(self, user, action, item):
        if action not in self._actions.keys():
            raise ActionNotFound('Invalid action: "%s"' % action)

        self.audit.user = str(user)
        self.audit.action = self._actions[action]
        self.audit.item = str(item)
        self.audit.save()

        msg = 'User (%s) %s: %s' % (str(user),
                                    self._actions[action],
                                    str(item))

        syslog.syslog(syslog.LOG_INFO, msg)
