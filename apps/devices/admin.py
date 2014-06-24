from django.contrib import admin
from apps.devices.models import Device, DeviceStatus


class DeviceStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'conversion')


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'system_node_key', 'pbbte_bridge_mac', 'ip', 'software_version', 'device_type')
    list_filter = ('software_version', 'device_type')
    search_fields = ('name', 'system_node_key', 'pbbte_bridge_mac', 'ip', 'software_version', 'device_type')


admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceStatus, DeviceStatusAdmin)