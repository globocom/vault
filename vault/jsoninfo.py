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
        if status == 500:
            log.error('Error on {}\'s menu info: {}'.format(
                    type(self).__name__,
                    self._menu["error"]))
        content = self._menu
        return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)

    @property
    def widget_info(self):
        self.validate_widget_info()
        status = 500 if "error" in self._widgets else 200
        if status == 500:
            log.error('Error on {}\'s widget info: {}'.format(
                    type(self).__name__,
                    self._widgets["error"]))
        content = self._widgets
        return HttpResponse(json.dumps(content),
                        content_type='application/json',
                        status=status)

    @property
    def all_info(self):
        self.generate_menu_info()
        self.validate_widget_info()
        status = 200
        if "error" in self._menu:
            status = 500
            log.error('Error on {}\'s menu info: {}'.format(
                    type(self).__name__,
                    self._menu["error"]))
        if "error" in self._widgets:
            status = 500
            log.error('Error on {}\'s widget info: {}'.format(
                    type(self).__name__,
                    self._widgets["error"]))
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
            widget["type"] = widget.get("type", "default")
            widget["name"] = widget.get("name", type(self).__name__)
            widget["title"] = widget.get("title", "")
            widget["subtitle"] = widget.get("subtitle",
                    type(self).__module__.split('.')[0])
            widget["color"] = self.translate_color(widget.get("color"))
            widget["icon"] = widget.get("icon", "far fa-question-circle")
            widget["url"] = widget.get("url", "/")
            widget["properties"] = widget.get("properties", [])
            widget["buttons"] = widget.get("buttons", [])
            for prop in widget["properties"]:
                prop["name"] = prop.get("name", "")
                prop["description"] = prop.get("description", "")
                prop["value"] = prop.get("value", "")
            for button in widget["buttons"]:
                button["name"] = button.get("name", "")
                button["url"] = button.get("url", "/")

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
