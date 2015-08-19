
from unittest import TestCase
from mock import patch

from dashboard.widgets import BaseWidget


class TestWidget(BaseWidget):
    title = "Test Title"
    subtitle = "Test SubTitle"
    description = "Test Description"

    def get_widget_context(self):
        return {'widget_variable': 'test_variable'}


class WidgetsTest(TestCase):

    def setUp(self):
        self.testwidget = TestWidget({})

    def test_new_widget_require_an_initial_context_parameter(self):
        self.assertRaises(TypeError, TestWidget)

    def test_widget_base_class_is_basewidget(self):
        self.assertEquals(TestWidget.__base__, BaseWidget)

    def test_title_subtile_description_on_widget_render(self):
        widget_content = self.testwidget.render()
        self.assertIn("Test Title", widget_content)
        self.assertIn("Test SubTitle", widget_content)
        self.assertIn("Test Description", widget_content)

    def test_custom_widget_context(self):
        context = self.testwidget._full_context()
        self.assertIn('widget_variable', context)
