# -*- coding: utf-8 -*-

import syslog
from .models import Audit


class ActionNotFound(Exception):
    pass


class ActionLogger:
    """ A wrapper to log actions """

    def __init__(self):
        self._actions = {
            "create": "Criou",
            "update": "Atualizou",
            "delete": "Removeu",
            "upload": "Realizou Upload",
            "download": "Realizou Download",
            "enable": "Habilitou",
            "disable": "Desabilitou",
            "restore": "Restaurou",
            "update_trash": "Atualizou a lixeira do container",
            "remove_cache": "Removeu do cache",
            "update header": "Atualizou Header",
            "set_private": "Setou container como privado",
            "set_public": "Setou container como publico",
        }

    def log(self, user, action, item):
        if action not in self._actions.keys():
            raise ActionNotFound("Invalid action: '{}'".format(action))

        audit = Audit(user=user,
                      action=self._actions[action],
                      item=str(item))
        audit.save()

        msg = self._make_log_message(user, action, item)
        syslog.syslog(syslog.LOG_INFO, msg)

    def _make_log_message(self, user, action, item):
        return 'Usuario {} {} {}'.format(user,
                                         self._actions[action],
                                         str(item))
