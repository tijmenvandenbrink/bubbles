from rest_framework import serializers
from apps.components.models import Component


class ComponentSerializer(serializers.HyperlinkedModelSerializer):
    device = serializers.HyperlinkedIdentityField(view_name="device-detail")

    class Meta:
        model = Component
        fields = ('url', 'name', 'device', 'speed')