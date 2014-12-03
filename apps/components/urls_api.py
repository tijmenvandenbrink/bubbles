from apps.components.views import ComponentViewSet

# API
component_list = ComponentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

component_detail = ComponentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})