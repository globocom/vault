# Vault

## Creating new apps

While Vault already delivers an app for Swift management and another for Keystone management, it also allows you to easily implement your own apps. This helps you centralize several services in a single, standardized web interface.

### What you need

In order to create an app for Vault, you'll need to create it as a Python package. You won't need to install libraries such as [Bootstrap](https://getbootstrap.com/) and [Font Awesome](https://fontawesome.com/), as your app will already have access to those due to being part of Vault.

### Decorators and Mixins

// TODO

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
