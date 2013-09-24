import logging

from django.core.management.base import BaseCommand, CommandError

from apps.organizations.models import Organization
from apps.services.models import Service, ServiceType, ServiceStatus

from apps.core.management.commands.surf_utils import SurfSoap
from apps.core.management.commands._surf_settings import *

logger = logging.getLogger(__name__)


def sync_objects(data):
    """ Reconciles all client records retrieved from IDD with the Bubbles database

    :param data: client records retrieved from IDD
    :type data: dictionary
    """
    for klant in data.keys():
        for service_id in data[klant].keys():
            obj = data[klant][service_id]
            logger.debug("RAW object from idd: {}".format(obj))
            if 'klant_id' in obj and 'int_id' in obj:
                org, created = Organization.objects.get_or_create(org_id=obj['klant_id'],
                                                                  defaults={'name': obj['klantnaam'],
                                                                            'org_abbreviation': obj['klantafkorting']})

                service, created = Service.objects.get_or_create(service_id=obj['int_id'],
                                                                 defaults={'name': obj['interfacenaam'],
                                                                           'description': obj['omschrijving'],
                                                                           'service_type': ServiceType.objects.get(
                                                                               name='IP Interface'),
                                                                           'status': ServiceStatus.objects.get(
                                                                               name='Production'),
                                                                           'cir': 0,
                                                                           'eir': obj['capaciteit_1'],
                                                                           'report_on': True})
                service.organization.add(org)
            elif 'klantid' in obj and 'service_id' in obj:
                org, created = Organization.objects.get_or_create(org_id=obj['klantid'],
                                                                  defaults={'name': obj['klantnaam'],
                                                                            'org_abbreviation': obj['klantafkorting']})

                service, created = Service.objects.get_or_create(service_id=obj['service_id'],
                                                                 defaults={'name': obj['service_id'],
                                                                           'description': obj['omschrijving'],
                                                                           'service_type': ServiceType.objects.get(
                                                                               name='LP Interface'),
                                                                           'status': ServiceStatus.objects.get(
                                                                               name='Production'),
                                                                           'cir': obj['capaciteit_prov'],
                                                                           'eir': obj['capaciteit_kv'],
                                                                           'report_on': True})
                service.organization.add(org)
            else:
                logger.error("We found a strange object in IDD: {}".format(obj))
                continue

            if created:
                logger.info("Created service: {}".format(service))
            elif not created:
                logger.info("Service already exists: {}".format(service))


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
            ('lp', 'LP Interface'),
            # Tunnel types
            ('tu', 'Tunnel Unprotected'),
            ('tp', 'Tunnel Protected'),
            ('tdh', 'Tunnel Dual-homed'),
            # Low level types
            ('lag', 'LAG'),
            ('port', 'Port'),
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
            ServiceType.objects.get_or_create(name=v)

        for k, v in SERVICE_STATUS_CHOICES:
            ServiceStatus.objects.get_or_create(name=k, conversion=v)

        for k, v in IDD_URLS.items():
            data = SurfSoap(v['url'], v['backup_file'], k).getdata()
            sync_objects(data)

        logger.info('Successfully synced database')