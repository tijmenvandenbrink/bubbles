import logging
from optparse import make_option

from django.core.management.base import BaseCommand

from apps.organizations.models import Organization
from apps.services.models import Service, ServiceType, ServiceStatus

from apps.core.utils import update_obj
from apps.core.management.commands.surf_utils import SurfSoap
from apps.core.management.commands._surf_settings import *

logger = logging.getLogger(__name__)


def sync_objects(data):
    """ Reconciles all client records retrieved from IDD with the Bubbles database.

    :param data: client records retrieved from IDD
    :type data: dictionary
    """
    for klant in data.keys():
        for service_id in data[klant].keys():
            obj = data[klant][service_id]
            logger.debug("RAW object from idd: {}".format(obj))
            # IP Interfaces
            if 'klant_id' in obj and 'int_id' in obj:
                defaults = {'name': obj['klantnaam'], 'org_abbreviation': obj['klantafkorting']}
                org, created = Organization.objects.get_or_create(org_id=obj['klant_id'], defaults=defaults)
                org = update_obj(org, **defaults)
                if created:
                    logger.info('action="Organization create", status="Created", component="organization", '
                                'org_id="{org.org_id}", organization_name="{org.name}", '
                                'organization_abbreviation="{org.org_abbreviation}"'.format(org=org))
                else:
                    logger.info('action="Organization create", status="Updated", component="organization", '
                                'org_id="{org.org_id}", organization_name="{org.name}", '
                                'organization_abbreviation="{org.org_abbreviation}"'.format(org=org))

                defaults = {'name': obj['interfacenaam'], 'description': obj['omschrijving'],
                            'service_type': ServiceType.objects.get(name='IP Interface'),
                            'status': ServiceStatus.objects.get(name='Production'),
                            'cir': 0, 'eir': obj['capaciteit_1'],
                            'report_on': True}

                # todo: extract more exact ServiceType from service object
                service, created = Service.objects.get_or_create(service_id=obj['interfacenaam'], defaults=defaults)
                if created:
                    logger.info('action="Service create", status="Created", component="service", '
                                'service_name="{svc.name}", service_id="{svc.service_id}", '
                                'service_type="{svc.service_type}", service_status="{svc.status}").'.format(
                        svc=service))
                else:
                    logger.info('action="Service create", status="Updated", component="service", '
                                'service_name="{svc.name}", service_id="{svc.service_id}", '
                                'service_type="{svc.service_type}", service_status="{svc.status}").'.format(
                        svc=service))

                service.organization.add(org)
                service = update_obj(service, **defaults)
                logger.info('action="Relationship create", status="created", component="service", '
                            'service_name="{svc.name}", service_id="{svc.service_id}", '
                            'service_type="{svc.service_type}", service_status="{svc.status}"), '
                            'organization_name="{org.name}", organization_id="{org.org_id}, '
                            'organization_abbreviation="{org.org_abbreviation}""'.format(svc=service, org=org))

            # LP Interfaces
            elif 'klantid' in obj and 'service_id' in obj:
                defaults = {'name': obj['klantnaam'], 'org_abbreviation': obj['klantafkorting']}
                org, created = Organization.objects.get_or_create(org_id=obj['klantid'], defaults=defaults)
                org = update_obj(org, **defaults)
                if created:
                    logger.info('action="Organization create", status="Created", component="organization", '
                                'org_id="{org.org_id}", organization_name="{org.name}", '
                                'organization_abbreviation="{org.org_abbreviation}"'.format(org=org))
                else:
                    logger.info('action="Organization create", status="Updated", component="organization", '
                                'org_id="{org.org_id}", organization_name="{org.name}", '
                                'organization_abbreviation="{org.org_abbreviation}"'.format(org=org))

                services = Service.objects.filter(service_id__contains=obj['service_id'])
                if services.count() == 0:
                    logger.warning('action="Service get", status="ServiceDoesNotExist", result="The service was not '
                                   'found in the Bubbles database, but does exist in IDD. Please investigate", '
                                   'component="service", service_id="{service_id}", '
                                   'service_description="{description}"'.format(service_id=obj['service_id'],
                                                                                description=obj["omschrijving"]))
                    continue

                # Connect the services to the organization
                for service in services:
                    defaults = {'status': ServiceStatus.objects.get(name='Production'),
                                'cir': obj['capaciteit_prov'], 'eir': obj['capaciteit_kv'], 'report_on': True}
                    service.organization.add(org)
                    service = update_obj(service, **defaults)
                    logger.info('action="Relationship create", status="created", component="service", '
                                'service_name="{svc.name}", service_id="{svc.service_id}", '
                                'service_type="{svc.service_type}", service_status="{svc.status}"), '
                                'organization_name="{org.name}", organization_id="{org.org_id}", '
                                'organization_abbreviation="{org.org_abbreviation}""'.format(svc=service, org=org))

            else:
                logger.error('action="Identify IDD object", status="Failed", result="This object will not be synced", '
                             'object={}'.format(obj))
                continue


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--skip-sync-objects',
                                                         action='store_true',
                                                         dest='sync_objects',
                                                         default=False,
                                                         help='Skip syncing objects from IDD'),
    )

    args = ""
    help = "Synchronizes the Bubbles database with SURFnet IDD"

    def handle(self, *args, **options):
        for k, v in IDD_URLS.items():
            data = SurfSoap(v['url'], v['backup_file'], k).getdata()
            if options['sync_objects']:
                logger.info('action="Skip syncing objects from IDD with Bubbles"')
            else:
                logger.info('action="Syncing objects from IDD with Bubbles"')
                sync_objects(data)