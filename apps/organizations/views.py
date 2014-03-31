from django.shortcuts import render, get_object_or_404
from apps.organizations.models import Organization


def organizations_list(request):
    organization_list = Organization.objects.all().order_by('name')
    return render(request, 'organizations.html', {"organization_list": organization_list})


def organization_detail(request, org_id):
    organization = get_object_or_404(Organization, org_id=org_id)
    return render(request, 'organization_detail.html', {"organization": organization})