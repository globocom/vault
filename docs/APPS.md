# Vault

## Creating new apps

While Vault already delivers an app for Swift management and another for Keystone management, it also allows you to easily implement your own apps. This helps you centralize several services in a single, standardized web interface.

### What you need

In order to create an app for Vault, you'll need to create it as a Python package. You won't need to install libraries such as [Bootstrap](https://getbootstrap.com/) and [Font Awesome](https://fontawesome.com/), as your app will already have access to those due to being part of Vault.

For more information on how to transform your Django app into a Python package, see [Django's documentation on packaging apps](https://docs.djangoproject.com/en/3.0/intro/reusable-apps/#packaging-your-app).

### Decorators and Mixins

When creating your views, Django already offers decorators (for function-based views) and mixins (for class-based views) to help you, such as limiting its access to logged users through the [login_required decorator](https://docs.djangoproject.com/en/3.0/topics/auth/default/#the-login-required-decorator) or the [LoginRequired mixin](https://docs.djangoproject.com/en/3.0/topics/auth/default/#the-loginrequired-mixin).

Vault offers its own decorators and mixins to help you develop your views. One thing that is mandatory is that your views require the user to have a project selected before being given access to them. For that situation, use the `vault.utils.project_required` decorator; in case of a class-based view, use the `vault.views.ProjectCheckMixin`. For more information, see [Django's documentation on decorating a class](https://docs.djangoproject.com/en/3.0/topics/class-based-views/intro/#decorating-the-class).

Example:

``` python
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from vault.utils import project_required

class MyView(LoginRequiredMixin, View):

    template_name = 'my_template.html'

    @method_decorator(project_required)
    def get(self, request, *args, **kwargs):

        return render()

```

In case your view must be restricted to superusers, you can use the `vault.views.SuperUserMixin` mixin.

### Templates

When creating your app's pages, it is necessary to extend Vault's base template. To do that, simply begin your templates with: `{% extends "vault/base.html" %}`

You can then override the contents of your page by using blocks. See [Django's documentation on template inheritance](https://docs.djangoproject.com/en/3.0/ref/templates/language/#template-inheritance) for more information.

Example:

``` html
{% extends "vault/base.html" %}

{% load i18n static %}

{% block title %}My App{% endblock %}
{% block content_title %}My App{% endblock %}

{% block css %}
  <link rel="stylesheet" type="text/css" href="{% static 'myapp/css/hello.css' %}" />
{% endblock %}

{% block content %}

<div class="card">
  <div class="card-body">
    <p>This button leads to Vault's home:</p>
    <a href="{% url "dashboard" %}" class="create-project btn btn-primary">
      <i class="fa fa-home"></i>
    </a>
  </div>
</div>

{% endblock %}

{% block js_bottom %}
<script>
  alert("Hello there.");
</script>
{% endblock %}
```

### Installing your app

Install your app as a Python package, then append its name to the end of vault/settings.py's `INSTALLED_APPS` list. Then, your app's URLs will be accessible at /p/&lt;selected_project&gt;/&lt;your_app_name&gt;/. You can access the selected project in your views by accessing the `project` argument.

### Creating a widget and/or sidebar menu

After your app is installed and its views are accessible, you'll need a way to visit them via Vault's main page. For that purpose, you must create an item in the sidebar menu and, optionally, one or more widgets that show some important information and shortcut buttons.

To do that, you must create a class that extends from `vault.jsoninfo.JsonInfo` and overrides its `generate_menu_info` and `generate_widget_info`, respectively.

- `generate_menu_info` must return a dictionary in the following format:
``` python
{
    "name": "My Service",
    "icon": "far fa-question-circle", # The class of a Font Awesome icon
    "url": reverse("myapp_main_page", kwargs={'project': project_name}),
}
```

- `generate_widget_info` must return a list of dictionaries, each representing a widget, in the following format:
``` python
[
    {
        "name": "myapp", # this is used to differentiate your widget in the CSS
        "title": "MyApp", # the technology behind the service, i.e Keystone
        "subtitle": "My Service", # the service itself, i.e Identity Service
        "color": "green", # the color of your widget, defaults to gray
        "icon": "fas fa-key", # The class of a Font Awesome icon
        "properties": [
            {
                "description": "", # text above the value
                "value": 50 # value of something important
                "name": "important things", # text below the value
            }
        ],
        "buttons": [
            {
                "name": "Things",
                "url": reverse("myapp_list_things", kwargs={'project': project_name})
            }
        ]
    }
]
```

Then, make a view that, on a get request, instantiates that class and returns its `render()` method. Since all URLs will require the user's current project, you can access it from your instance's `self.request.session` variable. Your view can also be exclusive to specific users, such as superusers or users in a specific team, making other users unable to see the your app's menu item and widgets.

Ex:

``` python
from vault.jsoninfo import JsonInfo

class MyAppJsonInfo(JsonInfo):
    def generate_menu_info(self):
        project_name = self.request.session.get('project_name')
        return {
            "name": "My Service",
            "icon": "far fa-question-circle",
            "url": reverse("myapp_main_page", kwargs={'project': project_name}),
        }

    def generate_widget_info(self):
        project_name = self.request.session.get('project_name')
        return [
            {
                "name": "myapp",
                "title": "MyApp",
                "subtitle": "My Service",
                "color": "green",
                "icon": "fas fa-key",
                "properties": [
                    {
                        "description": "",
                        "value": 50
                        "name": "important things",
                    }
                ],
                "buttons": [
                    {
                        "name": "Things",
                        "url": reverse("myapp_list_things", kwargs={'project': project_name})
                    }
                ]
            }
        ]


@utils.project_required
@login_required
def info_json(request, project=None):
    info = MyAppJsonInfo(request=request)

    return info.render(request)
```

Finally, you must create the URL for your view. It must be added to your `urls.py` file exactly as follows:

``` python
# ...
url(r'^api/info$', views.info_json, name="info_json"),
# ...
```

## Bonus Features

### Pagination

If your app has a page that lists items and you need to paginate those items, you can use Vault's own pagination feature. To use it, do the following:

- Import `generic_pagination` from `vault.utils`;
- Get the current page from `request.GET`, defaulting it to 1;
- Add your list of items to the context by using the `generic_pagination` function.

Example:
``` python
from vault.utils import generic_pagination

# ...

def my_view(request, project):

    my_items = get_item_list()

    # ...

    page = request.GET.get('page', 1)

    context = {
        # ...
        'items': utils.generic_pagination(my_items, page),
    }

    return render(request, 'my_template.html', context)
```

Once that's done on your view, you need to add the pagination Template Tag to your template. For more information on Template Tags, refer to [Django's documentation](https://docs.djangoproject.com/en/3.0/howto/custom-template-tags/). Here's an example of a template using Vault's pagination:

``` html
{% extends "vault/base.html" %}

{% load i18n static pagination %}

{% block content %}

<div class="vault-table-container">
  <table id="container-list" class="table table-bordered table-striped table-hover">
    <thead>
      <tr>
        <th>Name</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
    {% for item in items %}
      <tr>
        <td>item.name</td>
        <td>item.value</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
</div>

{% pagination items %}

{% endblock %}
```
