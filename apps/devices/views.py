from django.shortcuts import render, render_to_response, get_object_or_404
from apps.devices.models import Device


def devices_list(request):
    device_list = Device.objects.all().order_by('name')
    return render(request, 'devices.html', {"device_list": device_list})


def device_detail(request, device_name):
    device = get_object_or_404(Device, name__iexact=device_name)
    return render(request, 'device_detail.html', {"device": device})