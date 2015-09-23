# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin

from vault.views import SetProjectView, OAuthVaultCallback, \
                        OAuthVaultRedirect, VaultLogout


urlpatterns = patterns('',
    url(r'^', include('dashboard.urls')),
    url(r'^', include('identity.urls')),

    # Swift
    url(r'^storage/', include('swiftbrowser.urls')),

    # sobreescrevendo admin:logout devido ao redirect loop gerado pelo
    # backstage_accounts (precisa ficar antes das urls do admin)
    url(r'^admin/logout/$', VaultLogout.as_view(), name='vault_logout'),

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
