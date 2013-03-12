from django.contrib import admin
from apps.components.models import Component


class ComponentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Component, ComponentAdmin)