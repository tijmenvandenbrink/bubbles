from apps.services.views import ServiceViewSet, ServiceStatusViewSet, ServiceTypeViewSet

# API
service_list = ServiceViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

service_detail = ServiceViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

servicestatus_list = ServiceStatusViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

servicestatus_detail = ServiceStatusViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

servicetype_list = ServiceTypeViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

servicetype_detail = ServiceTypeViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})