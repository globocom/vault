# -*- coding: utf-8 -*-

from unittest import TestCase

from dashboard.widgets import BaseWidget


class TestWidget(BaseWidget):

    def get_widget_context(self):
        return {'widget_variable': 'test_variable'}


class WidgetsTest(TestCase):

    def setUp(self):
        self.testwidget = TestWidget({})

    def test_new_widget_require_an_initial_context_parameter(self):
        self.assertRaises(TypeError, TestWidget)

    def test_widget_base_class_is_basewidget(self):
        self.assertEquals(TestWidget.__base__, BaseWidget)

    def test_custom_widget_context(self):
        context = self.testwidget._full_context()
        self.assertIn('widget_variable', context)
