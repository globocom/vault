# -*- coding:utf-8 -*-

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from vault.views import SetProjectView, OAuthVaultCallback, \
                        OAuthVaultRedirect


urlpatterns = patterns('',
    # url(r'', include('backstage_accounts.urls')),
    url(r'^', include('dashboard.urls')),
    url(r'^', include('identity.urls')),
    url(r'^storage/', include('swiftbrowser.urls')),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # OAuthCallback
    url(r'^admin/vault/callback/(?P<provider>backstage)/$',
       OAuthVaultCallback.as_view(),
       name='allaccess-callback'),

    # OAuthLogin
    url(r'^admin/vault/login/(?P<provider>backstage)/$',
       OAuthVaultRedirect.as_view(),
       name='allaccess-login'),

    # set project_id session
    url(r'^set-project/(?P<project_id>[\w\-]+)/?$', SetProjectView.as_view(),
        name='set_project'),
)
