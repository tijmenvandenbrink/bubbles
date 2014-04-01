from django.shortcuts import render, get_object_or_404
from django.core.paginator import PageNotAnInteger, EmptyPage

from apps.services.models import Service
from apps.statistics.models import DataSource
from apps.core.utils import create_multibarchart
from apps.core.diggpaginator import DiggPaginator


def services_list(request):
    services = Service.objects.all().prefetch_related('organization', 'status', 'service_type').order_by('name')

    paginator = DiggPaginator(services, 25, body=10, padding=2, margin=2, )
    page = request.GET.get('page')

    try:
        service_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        service_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        service_list = paginator.page(paginator.num_pages)

    return render(request, 'services.html', {"service_list": service_list})


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)

    datasources = DataSource.objects.filter(name__contains="Volume")
    data = create_multibarchart(service, datasources)

    return render(request, 'service_detail.html', {"service": service, "data": data,})