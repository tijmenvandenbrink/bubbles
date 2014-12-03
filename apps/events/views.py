from django.shortcuts import render
from apps.events.models import Event, EventClass, EventSeverity
from rest_framework import viewsets
from apps.events.serializers import EventSerializer, EventClassSerializer, EventSeveritySerializer


def events_list(request):
    return render(request, 'events.html', {"active": "events"})


class EventSeverityViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = EventSeverity.objects.all()
    serializer_class = EventSeveritySerializer


class EventClassViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = EventClass.objects.all()
    serializer_class = EventClassSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer