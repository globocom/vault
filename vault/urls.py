# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin

from vault.views import SetProjectView


urlpatterns = patterns('',
    url(r'^', include('dashboard.urls')),
    url(r'^', include('identity.urls')),

    url(r'^login/$', 'vault.views.login_user'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
                          {'next_page': '/login/'}),

    # Swift
    url(r'^storage/', include('swiftbrowser.urls')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # set project_id session
    url(r'^set-project/(?P<project_id>[\w\-]+)/?$', SetProjectView.as_view(),
        name='set_project'),
)
