import logging
import requests
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from vault import utils
from actionlogger.actionlogger import ActionLogger
from storage.forms import RemoveCacheForm

log = logging.getLogger(__name__)
actionlog = ActionLogger()


@utils.project_required
@login_required
def storage_cache(request, project):
    context = {}
    return render(request, 'storage/cache.html', context)


@utils.project_required
@login_required
def remove_from_cache(request, project):
    form = RemoveCacheForm(request.POST or None)

    if form.is_valid():
        urls = form.cleaned_data['urls'].splitlines()

        data = {
            'url': urls,
            'user': request.user.username
        }

        api_url = '{host}/url/add'.format(host=settings.CACHESWEEP_API)
        req = requests.post(api_url, json=data)

        if req.status_code == 201:
            messages.add_message(request, messages.SUCCESS,
                _('URLs scheduled to be removed. Grab some coffee, it takes 2 to 3 minutes to remove.'))

            form = RemoveCacheForm(None)
            actionlog.log(request.user.username, "remove_cache", repr(urls))
        else:
            messages.add_message(request, messages.ERROR,
                _('Fail to schedule URLs to be removed.'))

    context = utils.update_default_context(request, {'form': form})

    return render(request, 'storage/cache_remove.html', context)


@utils.project_required
@login_required
def add_to_cache(request, project):
    context = {'pre_cache_api_url': ''}
    if hasattr(settings, 'PRE_CACHE_API'):
        context['pre_cache_api_url'] = settings.PRE_CACHE_API

    return render(request, 'storage/cache_add.html', context)
