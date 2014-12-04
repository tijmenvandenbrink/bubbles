from django.views.generic import ListView, DetailView

from rest_framework import viewsets, permissions
from braces.views import OrderableListMixin
from digg_paginator import DiggPaginator

from apps.devices.models import Device, DeviceStatus
from apps.devices.serializers import DeviceSerializer, DeviceStatusSerializer


class DeviceList(OrderableListMixin, ListView):
    model = Device
    orderable_columns = (u"name", u"description",)
    orderable_columns_default = u"name"
    template_name = 'devices.html'
    context_object_name = 'device_list'
    paginate_by = 20
    paginator_class = DiggPaginator


class DeviceDetail(DetailView):
    model = Device
    context_object_name = 'device'
    template_name = 'device_detail.html'
    slug_field = 'name'


class DeviceStatusViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = DeviceStatus.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DeviceStatusSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = Device.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = DeviceSerializer