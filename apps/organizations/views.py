from django.shortcuts import render, get_object_or_404

from django.views.generic import ListView, DetailView
from braces.views import OrderableListMixin, PrefetchRelatedMixin
from rest_framework import viewsets
from digg_paginator import DiggPaginator

from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer


class OrganizationList(OrderableListMixin, ListView):
    model = Organization
    orderable_columns = (u"name",)
    orderable_columns_default = u"name"
    template_name = 'organizations.html'
    context_object_name = 'organization_list'
    paginate_by = 20
    paginator_class = DiggPaginator


class OrganizationDetail(PrefetchRelatedMixin, DetailView):
    model = Organization
    prefetch_related = [u"services", u"services__status", u"services__service_type", u"services__organization"]
    context_object_name = 'organization'
    template_name = 'organization_detail.html'
    slug_field = 'org_id'


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer