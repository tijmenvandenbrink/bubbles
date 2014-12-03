from rest_framework import serializers
from apps.services.models import Service, ServiceStatus, ServiceType
from apps.organizations.models import Organization


class ServiceTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceType
        fields = ('url', 'name')


class ServiceStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ServiceStatus
        fields = ('url', 'name', 'conversion')


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.HyperlinkedRelatedField(queryset=ServiceStatus.objects.all(), view_name='servicestatus-detail')
    service_type = serializers.HyperlinkedRelatedField(queryset=ServiceType.objects.all(), view_name='servicetype-detail')
    organization = serializers.HyperlinkedRelatedField(many=True, queryset=Organization.objects.all(),
                                                       view_name='organization-detail')

    class Meta:
        model = Service
        fields = ('url', 'name', 'description', 'service_id', 'cir', 'eir', 'report_on', 'status', 'service_type',
                  'organization')