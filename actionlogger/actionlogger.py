# -*- coding:utf-8 -*-

import syslog


class ActionNotFound(Exception):
    pass


class ActionLogger(object):
    """ A wrapper to log actions """

    def __init__(self):
        self._actions = {'create': 'CREATED',
                         'update': 'UPDATED',
                         'delete': 'DELETED'}

    def log(self, user, action, item):
        if action not in self._actions.keys():
            raise ActionNotFound('Invalid action: "%s"' % action)

        msg = 'User (%s) %s: %s' % (str(user),
                                    self._actions[action],
                                    str(item))

        syslog.syslog(syslog.LOG_INFO, msg)

    
    def savedb(self, user, action, item):
    
        audit = Audit(user=request.user, action=action, item=item)   
        audit.save()
