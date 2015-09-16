# -*- coding: utf-8 -*-

from vault.models import *
#from allaccess.admin import AccountAccess, Provider
from django.contrib import admin

admin.site.register(Area)
admin.site.register(GroupProjects)
admin.site.register(AreaProjects)
#admin.site.unregister(AccountAccess)
#admin.site.unregister(Provider)
