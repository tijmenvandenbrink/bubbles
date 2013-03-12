from django.contrib import admin
from apps.devices.models import Device


class DeviceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Device, DeviceAdmin)