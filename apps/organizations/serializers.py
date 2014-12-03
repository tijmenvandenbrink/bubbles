from rest_framework import serializers
from apps.organizations.models import Organization


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    services = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='service-detail')

    class Meta:
        model = Organization
        fields = ('url', 'name', 'org_id', 'org_abbreviation', 'services')