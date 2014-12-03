from apps.devices.views import DeviceViewSet, DeviceStatusViewSet
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

# API
device_list = DeviceViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

device_detail = DeviceViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

# API
status_list = DeviceStatusViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

status_detail = DeviceStatusViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})