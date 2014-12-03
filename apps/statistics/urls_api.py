from apps.statistics.views import DataSourceViewSet, DataPointViewSet

# API
datasource_list = DataSourceViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

datasource_detail = DataSourceViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

# API
datapoint_list = DataPointViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

datapoint_detail = DataPointViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})