from django.shortcuts import render, get_object_or_404

from apps.services.models import Service
from apps.statistics.models import DataSource
from apps.core.utils import create_multibarchart


def services_list(request):
    service_list = Service.objects.all().prefetch_related('organization',
                                                          'status',
                                                          'service_type').order_by('name')
    return render(request, 'services.html', {"service_list": service_list})


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)

    datasources = DataSource.objects.filter(name__contains="Volume")
    data = create_multibarchart(service, datasources)

    return render(request, 'service_detail.html', {"service": service, "data": data,})