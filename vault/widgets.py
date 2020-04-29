from django.forms.widgets import PasswordInput


class PasswordInputWithEye(PasswordInput):

    def __init__(self, attrs=None, render_value=False):
        super().__init__(attrs=attrs, render_value=render_value)
        self.template_name = 'vault/forms/widgets/password.html'
