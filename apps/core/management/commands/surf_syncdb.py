from django.core.management.base import BaseCommand, CommandError

from apps.organizations.models import Organization
from apps.services.models import Service, ServiceType, ServiceStatus

from apps.core.management.commands._surf_utils import SurfSoap
from apps.core.management.commands._surf_settings import *


class Command(BaseCommand):
    args = "no arguments needed"
    help = "Synchronizes the Django db with surfnet idd"

    def handle(self, *args, **options):

        # Fixture for adding Service types
        SERVICE_TYPE_CHOICES = (
            # Customer service types
            ('sipu', 'Static IP Unprotected (VRRP)'),
            ('sipp', 'Static IP Protected (VRRP)'),
            ('dipu', 'Dynamic IP Unprotected (BGP)'),
            ('dipp', 'Dynamic IP Protected (BGP)'),
            ('slpu', 'Static LP (Unprotected)'),
            ('slpp', 'Static LP (Protected)'),
            ('slpr', 'Static LP (Resilient)'),
            ('dlpu', 'Dynamic LP (Unprotected)'),
            ('dlpp', 'Dynamic LP (Protected)'),
            ('dlpr', 'Dynamic LP (Resilient)'),
            ('ip', 'IP Interface'),
            # Tunnel types
            ('tu', 'Tunnel Unprotected'),
            ('tp', 'Tunnel Protected'),
            ('tdh', 'Tunnel Dual-homed'),
            # Low level types
            ('lag', 'LAG'),
            ('link', 'Link'),
            # Unknown
            ('unknown', 'Unknown')
        )

        # Fixture for adding Service types
        SERVICE_STATUS_CHOICES = (
            ('Production', 1000),
            ('Pre-production', 500),
            ('Test', 400),
            ('Maintenance', 300),
            ('Reserved', 100),
            ('Decommisioned', -1),
        )

        for k, v in SERVICE_TYPE_CHOICES:
            try:
                ServiceType.objects.get(name=v)
            except ServiceType.DoesNotExist:
                servicetype = ServiceType(name=v)
                servicetype.save()

        for k, v in SERVICE_STATUS_CHOICES:
            try:
                ServiceStatus.objects.get(name=k)
            except ServiceStatus.DoesNotExist:
                servicestatus = ServiceStatus(name=k, conversion=v)
                servicestatus.save()

        def _add_or_get_organization(klant_id):
            try:
                org = Organization.objects.get(org_id=klant_id)
                return org
            except Organization.DoesNotExist:
                org = Organization(name=klant, org_id=klant_id, org_abbreviation=obj['klantafkorting'])
                org.save()
                return org

        try:
            data = SurfSoap(GETINTERFACELIST_URL, INT_IDD_BACKUP).getdata()
        except:
            raise CommandError('Unable to connect to IDD...')

        for klant in data.keys():
            for service in data[klant].keys():
                obj = data[klant][service]
                if 'klant_id' in obj and 'int_id' in obj:
                    org = _add_or_get_organization(obj['klant_id'])
                    service = Service(name=obj['interfacenaam'],
                                      description=obj['omschrijving'],
                                      organization=org,
                                      service_id=obj['int_id'],
                                      type=ServiceType.objects.get(name='IP Interface'),
                                      status=ServiceStatus.objects.get(name='Production'),
                                      cir=0,
                                      eir=obj['capaciteit_1'])
                    service.save()
                elif 'klantid' in obj and 'service_id' in obj:
                    org = _add_or_get_organization(obj['klantid'])
                    service = Service(name=obj['service_id'],
                                      description=obj['omschrijving'],
                                      organization=org,
                                      service_id=obj['service_id'],
                                      type=ServiceType.objects.get(name='Dynamic LP (Resilient)'),
                                      status=ServiceStatus.objects.get(name='Production'),
                                      cir=obj['capaciteit_prov'],
                                      eir=obj['capaciteit_kv'])
                    service.save()
                else:
                    continue
        self.stdout.write('Successfully synced database')
