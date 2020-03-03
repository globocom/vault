# -*- coding: utf-8 -*-

import logging
import json

from django.http import HttpResponse

log = logging.getLogger(__name__)


class JsonInfo:

    def __init__(self, *args, **kwargs):

        self._menu = {}
        self._widgets = []

    @property
    def menu_info(self):
        self.generate_menu_info()
        status = 500 if "error" in self._menu else 200
        content = self._menu
        return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)

    @property
    def widget_info(self):
        self.generate_widget_info()
        status = 500 if "error" in self._widgets else 200
        content = self._widgets
        return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)

    @property
    def all_info(self):
        self.generate_menu_info()
        self.generate_widget_info()
        status = 500 if "error" in self._menu or \
                        "error" in self._widgets else 200
        content = {
            "menu": self._menu,
            "widgets": self._widgets
        }
        return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)

    def generate_menu_info(self):
        # Method must be overriden
        pass

    def generate_widget_info(self):
        # Method must be overriden
        pass

    def render(self, request):
        option = request.GET.get("opt", "all").lower()
        if option == "menu":
            return self.menu_info
        elif option == "widgets":
            return self.widget_info
        elif option == "all":
            return self.all_info
        else:
            status = 400
            content = {
                "error": "Unknown option \"{}\"".format(option)
            }
            return HttpResponse(json.dumps(content),
                            content_type='application/json',
                            status=status)
