# -*- coding: utf-8 -*-

from django.conf.urls import re_path
from storage import views


urlpatterns = [
    # Trash: enable/disable Undelete
    re_path(r'^trash-container-config/(?P<container>.+?)$', views.config_trash_container, name="config_trash_container"),
    re_path(r'^trash-container-status/(?P<container>.+?)$', views.container_trash_status, name="container_trash_status"),

    # Backup
    re_path(r'^backup-container-config/(?P<container>.+?)$', views.config_backup_container, name="config_backup_container"),
    re_path(r'^backup-container-status/(?P<container>.+?)$', views.container_backup_status, name="container_backup_status"),

    # Restore
    re_path(r'^backup-restore/', views.backup_restore, name="backup_restore"),

    # ACL: make container public/private
    re_path(r'^acl-container-update/(?P<container>.+?)$', views.container_acl_update, name="container_acl_update"),
    re_path(r'^acl-container-status/(?P<container>.+?)$', views.container_acl_status, name="container_acl_status"),

    # Cache
    re_path(r'^cache/?$', views.storage_cache, name="storage_cache"),
    re_path(r'^cache/remove/?$', views.remove_from_cache, name="remove_from_cache"),
    re_path(r'^cache/add/?$', views.add_to_cache, name="add_to_cache"),

    # Trash
    re_path(r'^trash/restore/', views.restore_object, name="restore_object"),
    re_path(r'^trash/remove/', views.remove_from_trash, name="remove_from_trash"),
    re_path(r'^trash/(?P<container>.+?)/(?P<prefix>(.+)+)?$', views.get_deleted_objects, name="deleted_objects"),

    # Storage urls
    re_path(r'^account/?$', views.accountview, name="accountview"),
    re_path(r'^objects/(?P<container>.+?)/(?P<prefix>(.+)+)?$', views.objectview, name="objectview"),
    re_path(r'^object/(?P<container>.+?)/(?P<objectname>.+?)$', views.object_item, name="object"),
    re_path(r'^upload/(?P<container>.+?)/(?P<prefix>.+)?$', views.upload, name="upload"),
    re_path(r'^create_object/(?P<container>.+?)/(?P<prefix>.+)?$', views.create_object, name="create_object"),
    re_path(r'^create_pseudofolder/(?P<container>.+?)/(?P<prefix>.+)?$', views.create_pseudofolder, name="create_pseudofolder"),
    re_path(r'^delete_container/(?P<container>.+?)$', views.delete_container_view, name="delete_container"),
    re_path(r'^delete/(?P<container>.+?)/(?P<objectname>.+?)$', views.delete_object_view, name="delete_object"),
    re_path(r'^delete_pseudofolder/(?P<container>.+?)/(?P<pseudofolder>.+?)$', views.delete_pseudofolder, name="delete_pseudofolder"),
    re_path(r'^create_container/?$', views.create_container, name="create_container"),
    re_path(r'^acls/(?P<container>.+?)/$', views.edit_acl, name="edit_acl"),
    re_path(r'^cors/(?P<container>.+?)/$', views.edit_cors, name="edit_cors"),
    re_path(r'^download/(?P<container>.+?)/(?P<objectname>.+?)$', views.download, name="download"),
    re_path(r'^preview/(?P<container>.+?)/(?P<objectname>.+?)$', views.download, name="preview"),
    re_path(r'^metadata/(?P<container>.+?)/(?P<objectname>.+?)?$', views.metadataview, name="metadata"),
    re_path(r'^custom-metadata/(?P<container>.+?)/(?P<objectname>.+?)?$', views.edit_custom_metadata, name="edit_custom_metadata"),
    re_path(r'^cache-control/(?P<container>.+?)/(?P<objectname>.+?)?$', views.cache_control, name="cache_control"),
    re_path(r'^versioning/(?P<container>.+?)/(?P<prefix>(.+)+)?$', views.object_versioning, name="object_versioning"),
    re_path(r'^optional-headers/(?P<container>.+?)/(?P<objectname>.+?)?$', views.optional_headers, name="optional_headers"),
    # API
    re_path(r'^api/info$', views.info_json, name="info_json"),
    re_path(r'^api/backup-list/?', views.container_backup_list, name="container_backup_list"),

    # Storage base url (/)
    re_path(r'^', views.containerview, name="containerview")
]
