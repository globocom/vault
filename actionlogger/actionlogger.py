# -*- coding:utf-8 -*-

import logging


class ActionNotFound(Exception):
    pass


class ActionLogger(object):
    """ A wrapper to log actions """

    def __init__(self, filename=None):

        if filename:
            logging.basicConfig(filename=filename, level=logging.INFO)

        self.logger = logging.getLogger('actionlogger')
        self._actions = {'create': 'CREATED',
                         'update': 'UPDATED',
                         'delete': 'DELETED'}

    def log(self, user, action, item):
        if action not in self._actions.keys():
            raise ActionNotFound('Invalid action: "%s"' % action)

        msg = 'User (%s) %s: %s' % (str(user),
                                    self._actions[action],
                                    str(item))
        self.logger.info(msg)
