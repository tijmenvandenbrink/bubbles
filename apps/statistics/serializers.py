from rest_framework import serializers
from apps.statistics.models import DataSource, DataPoint
from apps.services.models import Service


class DataSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataSource
        fields = ('url', 'name', 'description', 'unit', 'data_type', 'interval')


class DataPointSerializer(serializers.HyperlinkedModelSerializer):
    service = serializers.HyperlinkedRelatedField(queryset=Service.objects.all(), view_name='service-detail')
    data_source = serializers.HyperlinkedRelatedField(queryset=DataSource.objects.all(), view_name='datasource-detail')

    class Meta:
        model = DataPoint
        fields = ('url', 'start', 'end', 'value', 'service', 'data_source')