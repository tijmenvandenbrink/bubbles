from django.contrib import admin
from apps.components.models import Component


class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'device')
    search_fields = ('name', 'device')
    list_filter = ('device', 'name')


admin.site.register(Component, ComponentAdmin)