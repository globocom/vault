from vault.models import *
from django.contrib import admin

#class AccessInline(admin.TabularInline):
#    model = Access
#    extra = 0


admin.site.register(Area)
admin.site.register(GroupProjects)
admin.site.register(AreaProjects)

