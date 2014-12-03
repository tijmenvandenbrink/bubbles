from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from rest_framework import viewsets
from braces.views import OrderableListMixin
from digg_paginator import DiggPaginator

from apps.components.models import Component
from apps.components.serializers import ComponentSerializer


class ComponentList(OrderableListMixin, ListView):
    model = Component
    orderable_columns = (u"name", )
    orderable_columns_default = u"name"
    template_name = 'components.html'
    context_object_name = 'component_list'
    paginate_by = 20
    paginator_class = DiggPaginator


class ComponentDetail(DetailView):
    model = Component
    context_object_name = 'component'
    template_name = 'component_detail.html'


def components_list(request):
    components_list = Component.objects.all().prefetch_related('device')
    return render(request, 'components.html', {"components_list": components_list})


def component_detail(request, component_id):
    component = get_object_or_404(Component, pk=component_id)
    return render(request, 'component_detail.html', {"component": component})


class ComponentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer