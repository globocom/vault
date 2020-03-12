# -*- coding: utf-8 -*-

from django.conf.urls import url
from storage import views


urlpatterns = [
    # Trash: enable/disable Undelete
    url(r'^trash-container-config/(?P<container>.+?)$', views.config_trash_container, name="config_trash_container"),
    url(r'^trash-container-status/(?P<container>.+?)$', views.container_trash_status, name="container_trash_status"),

    # Backup
    url(r'^backup-container-config/(?P<container>.+?)$', views.config_backup_container, name="config_backup_container"),
    url(r'^backup-container-status/(?P<container>.+?)$', views.container_backup_status, name="container_backup_status"),

    # Restore
    url(r'^backup-restore/', views.backup_restore, name="backup_restore"),

    # ACL: make container public/private
    url(r'^acl-container-update/(?P<container>.+?)$', views.container_acl_update, name="container_acl_update"),
    url(r'^acl-container-status/(?P<container>.+?)$', views.container_acl_status, name="container_acl_status"),

    # Clear cache
    url(r'^cache/remove/', views.remove_from_cache, name="remove_from_cache"),

    # Trash
    url(r'^trash/restore/', views.restore_object, name="restore_object"),
    url(r'^trash/remove/', views.remove_from_trash, name="remove_from_trash"),
    url(r'^trash/(?P<container>.+?)/(?P<prefix>(.+)+)?$', views.get_deleted_objects, name="deleted_objects"),

    # Storage urls
    url(r'^objects/(?P<container>.+?)/(?P<prefix>(.+)+)?$', views.objectview, name="objectview"),
    url(r'^object/(?P<container>.+?)/(?P<objectname>.+?)$', views.object, name="object"),
    url(r'^upload/(?P<container>.+?)/(?P<prefix>.+)?$', views.upload, name="upload"),
    url(r'^create_object/(?P<container>.+?)/(?P<prefix>.+)?$', views.create_object, name="create_object"),
    url(r'^create_pseudofolder/(?P<container>.+?)/(?P<prefix>.+)?$', views.create_pseudofolder, name="create_pseudofolder"),
    url(r'^delete_container/(?P<container>.+?)$', views.delete_container_view, name="delete_container"),
    url(r'^delete/(?P<container>.+?)/(?P<objectname>.+?)$', views.delete_object_view, name="delete_object"),
    url(r'^delete_pseudofolder/(?P<container>.+?)/(?P<pseudofolder>.+?)$', views.delete_pseudofolder, name="delete_pseudofolder"),
    url(r'^create_container/?$', views.create_container, name="create_container"),
    url(r'^acls/(?P<container>.+?)/$', views.edit_acl, name="edit_acl"),
    url(r'^cors/(?P<container>.+?)/$', views.edit_cors, name="edit_cors"),
    url(r'^download/(?P<container>.+?)/(?P<objectname>.+?)$', views.download, name="download"),
    url(r'^preview/(?P<container>.+?)/(?P<objectname>.+?)$', views.download, name="preview"),
    url(r'^metadata/(?P<container>.+?)/(?P<objectname>.+?)?$', views.metadataview, name="metadata"),
    url(r'^custom-metadata/(?P<container>.+?)/(?P<objectname>.+?)?$', views.edit_custom_metadata, name="edit_custom_metadata"),
    url(r'^cache-control/(?P<container>.+?)/(?P<objectname>.+?)?$', views.cache_control, name="cache_control"),
    url(r'^versioning/(?P<container>.+?)/(?P<prefix>(.+)+)?$', views.object_versioning, name="object_versioning"),

    # API
    url(r'^api/info$', views.info_json, name="info_json"),
    url(r'^api/backup-list/?', views.container_backup_list, name="container_backup_list"),

    # Storage base url (/)
    url(r'^', views.containerview, name="containerview")
]
