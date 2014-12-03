from apps.events.views import EventViewSet, EventClassViewSet, EventSeverityViewSet

# API
event_list = EventViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

event_detail = EventViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

eventclass_list = EventClassViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

eventclass_detail = EventClassViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

eventseverity_list = EventSeverityViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

eventseverity_detail = EventSeverityViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})