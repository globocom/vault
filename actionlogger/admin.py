# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Audit


class AuditAdmin(admin.ModelAdmin):
    search_fields = ['user', 'action', 'item', 'through']


admin.site.register(Audit, AuditAdmin)
