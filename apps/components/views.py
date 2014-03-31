from django.shortcuts import render, get_object_or_404
from apps.components.models import Component


def components_list(request):
    components_list = Component.objects.all().prefetch_related('device')
    return render(request, 'components.html', {"components_list": components_list})


def component_detail(request, component_id):
    component = get_object_or_404(Component, pk=component_id)
    return render(request, 'component_detail.html', {"component": component})
