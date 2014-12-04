from django.shortcuts import render

from rest_framework import viewsets, permissions

from apps.statistics.models import DataSource, DataPoint
from apps.statistics.serializers import DataSourceSerializer, DataPointSerializer


def statistics_list(request):
    return render(request, 'statistics.html', {"active": "statistics"})


class DataSourceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = DataSource.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DataSourceSerializer


class DataPointViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = DataPoint.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DataPointSerializer