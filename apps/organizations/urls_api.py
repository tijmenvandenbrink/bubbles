from apps.organizations.views import OrganizationViewSet

# API
organization_list = OrganizationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

organization_detail = OrganizationViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})