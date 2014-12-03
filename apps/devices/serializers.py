from rest_framework import serializers
from apps.devices.models import Device, DeviceStatus


class DeviceStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeviceStatus
        fields = ('url', 'name', 'conversion')


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.HyperlinkedRelatedField(queryset=DeviceStatus.objects.all(), view_name='devicestatus-detail')

    class Meta:
        model = Device
        fields = ('url', 'name', 'system_node_key', 'pbbte_bridge_mac', 'device_type', 'ip', 'software_version',
                  'status')