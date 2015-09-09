# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from swiftbrowser import views

urlpatterns = patterns('swiftbrowser.views',

    url(r'^$',
        views.containerview, name="containerview"),

    url(r'^objects/(?P<container>.+?)/(?P<prefix>(.+)+)?$',
        views.objectview, name="objectview"),

    url(r'^upload/(?P<container>.+?)/(?P<prefix>.+)?$',
        views.upload, name="upload"),

    url(r'^create_object/(?P<container>.+?)/(?P<prefix>.+)?$',
        views.create_object, name="create_object"),

    url(r'^create_pseudofolder/(?P<container>.+?)/(?P<prefix>.+)?$',
        views.create_pseudofolder, name="create_pseudofolder"),

    url(r'^delete_container/(?P<container>.+?)$',
        views.delete_container_view, name="delete_container"),

    url(r'^delete/(?P<container>.+?)/(?P<objectname>.+?)$',
        views.delete_object_view, name="delete_object"),

    url(r'^delete_pseudofolder/(?P<container>.+?)/(?P<pseudofolder>.+?)$',
        views.delete_pseudofolder, name="delete_pseudofolder"),

    url(r'^create_container/?$',
        views.create_container, name="create_container"),

    url(r'^acls/(?P<container>.+?)/$',
        views.edit_acl, name="edit_acl"),

    url(r'^cors/(?P<container>.+?)/$',
        views.edit_cors, name="edit_cors"),

    url(r'^download/(?P<container>.+?)/(?P<objectname>.+?)$',
        views.download, name="download"),

    url(r'^metadata/(?P<container>.+?)/(?P<objectname>.+?)?$',
        views.metadataview, name="metadata"),

    # url(r'^versioning/(?P<container>.+?)/$',
    url(r'^versioning/(?P<container>.+?)/(?P<prefix>(.+)+)?$',
        views.object_versioning, name="object_versioning"),
)
