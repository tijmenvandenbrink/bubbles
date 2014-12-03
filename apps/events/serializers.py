from rest_framework import serializers
from apps.events.models import Event, EventClass, EventSeverity
from apps.services.models import Service
from apps.devices.models import Device
from apps.components.models import Component


class EventSeveritySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventSeverity
        fields = ('url', 'name', 'conversion')


class EventClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventClass
        fields = ('url', 'name')


class EventSerializer(serializers.HyperlinkedModelSerializer):
    event_class = serializers.HyperlinkedRelatedField(queryset=EventClass.objects.all(), view_name="eventclass-detail")
    severity = serializers.HyperlinkedRelatedField(queryset=EventSeverity.objects.all(), view_name="eventseverity-detail")
    service = serializers.HyperlinkedRelatedField(queryset=Service.objects.all(), required=False, allow_null=True, view_name="service-detail")
    device = serializers.HyperlinkedRelatedField(queryset=Device.objects.all(), required=False, allow_null=True, view_name="device-detail")
    component = serializers.HyperlinkedRelatedField(queryset=Component.objects.all(), required=False, allow_null=True, view_name="component-detail")

    class Meta:
        model = Event
        fields = ('url', 'description', 'start', 'end', 'event_class', 'severity', 'service',
                  'device', 'component')