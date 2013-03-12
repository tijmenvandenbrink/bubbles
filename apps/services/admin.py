from django.contrib import admin
from apps.services.models import Service, ServiceStatus, ServiceType


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'service_type', 'cir', 'eir')
    list_filter = ('organization', 'service_type')
    search_fields = ('name', 'description')


class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'conversion')


class ServiceTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceStatus, ServiceStatusAdmin)
admin.site.register(ServiceType, ServiceTypeAdmin)