# Vault

## Creating new apps

While Vault already delivers an app for Swift management and another for Keystone management, it also allows you to easily implement your own apps. This helps you centralize several services in a single, standardized web interface.

### What you need

In order to create an app for Vault, you'll need to create it as a Python package. You won't need to install libraries such as [Bootstrap](https://getbootstrap.com/) and [Font Awesome](https://fontawesome.com/), as your app will already have access to those due to being part of Vault.

For more information on how to transform your Django app into a Python package, see [Django's documentation on packaging apps](https://docs.djangoproject.com/en/3.0/intro/reusable-apps/#packaging-your-app).

### Decorators and Mixins

When creating your views, Django already offers decorators (for function-based views) and mixins (for class-based views) to help you, such as limiting its access to logged users through the [login_required decorator](https://docs.djangoproject.com/en/3.0/topics/auth/default/#the-login-required-decorator) or the [LoginRequired mixin](https://docs.djangoproject.com/en/3.0/topics/auth/default/#the-loginrequired-mixin).

Vault offers its own decorators and mixins to help you develop your views. One thing that is mandatory is that your views require the user to have a project selected before being given access to them. For that situation, use the `vault.utils.project_required` decorator; in case of a class-based view, use Django's `method_decorator` to apply that to the view's methods. For more information, see [Django's documentation on decorating a class](https://docs.djangoproject.com/en/3.0/topics/class-based-views/intro/#decorating-the-class).

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

        return

```

In case your view must be restricted to superusers, you can use the `vault.views.SuperUserMixin` mixin.

### Templates

When creating your app's pages, it is necessary to extend Vault's base template. To do that, simply begin your templates with: `{% extends "vault/base.html" %}`

You can then override the contents of your page by using blocks. See [Django's documentation on template inheritance](https://docs.djangoproject.com/en/3.0/ref/templates/language/#template-inheritance) for more information.

### Pagination

If your app has a page that lists items and you need to paginate those items, you can use Vault's own pagination feature. To use it, do the following:

- Import `generic_pagination` from `vault.utils`;
- Get the current page from `request.GET`, defaulting it to 1;
- Add your list of items to the context by using the `generic_pagination` function.

Example:
``` python
from vault.utils import generic_pagination

# ...

def my_view(request):

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

<div class="panel panel-default">
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

### Installing your app

Install your app as a Python package, then append its name to the end of vault/settings.py's `INSTALLED_APPS` list. From there, your app's URLs will already be accessible from Vault.

### Creating a widget and/or sidebar menu

// TODO
