# -*- coding:utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url

from vault.views import SetProjectView


urlpatterns = patterns('',
    url(r'', include('backstage_accounts.urls')),
    url(r'^', include('dashboard.urls')),
    url(r'^', include('identity.urls')),
    url(r'^storage/', include('swiftbrowser.urls')),

    # set project_id session
    url(r'^set-project/(?P<project_id>[\w\-]+)/?$', SetProjectView.as_view(),
        name='set_project'),
)
