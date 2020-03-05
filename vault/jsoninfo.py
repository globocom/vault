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
        self.validate_widget_info()
        status = 500 if "error" in self._widgets else 200
        content = self._widgets
        return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)

    @property
    def all_info(self):
        self.generate_menu_info()
        self.validate_widget_info()
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

    def translate_color(self, color):
        colors = {
            "blue": "#1e4794",
            "purple": "#622bab",
            "red": "#cc543f",
            "orange": "#b5821b",
            "yellow": "#bfb411",
            "green": "#688f10",
            "pink": "#a35aa3",
            "brown": "#7a5407",
            "gray": "#757575"
        }

        return colors.get(color, colors["gray"])

    def validate_widget_info(self):
        self.generate_widget_info()
        for widget in self._widgets:
            if 'color' in widget:
                widget['color'] = self.translate_color(widget['color'])

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
