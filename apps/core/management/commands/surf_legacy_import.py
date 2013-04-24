import logging
import pickle
import re
from datetime import datetime
import calendar

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import utc

from ....organizations.models import Organization
from ....services.models import Service
from ....statistics.models import DataSource, DataPoint
from ....core.management.commands._surf_settings import *
from ....core.utils import mkdate, get_derived_value

logger = logging.getLogger(__name__)


def process_file(filename):
    """

    :param filename: filename
    :type filename: string
    """
    with open(filename, 'r') as f:
        pkl = pickle.load(f)

    logger.info('Importing data from {}'.format(filename))
    m = re.match(r"\S+/(?P<report_type>(IP|LP)_Volume)_(?P<year>\d+)_(?P<month>\d+)_(customer|external).pkl", filename)

    start = datetime(int(m.group('year')), int(m.group('month')), 1).replace(tzinfo=utc)
    end = datetime(int(m.group('year')), int(m.group('month')),
                   calendar.monthrange(int(m.group('year')), int(m.group('month')))[1], 23, 59).replace(tzinfo=utc)

    for org_abbreviation in pkl:
        try:
            org = Organization.objects.get(org_abbreviation=org_abbreviation)
        except ObjectDoesNotExist:
            logger.warning('Organization {} does not exist'.format(org_abbreviation))
            # todo: Do we want to add non-existing organisations (old ones? faulty ones?)

        for service_id, value in pkl[org_abbreviation].items():
            for k, v in {0: "Volume in", 1: "Volume uit"}.items():
                ds = DataSource.objects.get(name=v)
                try:
                    service = Service.objects.get(name__iexact=service_id)
                    dp, created = DataPoint.objects.get_or_create(start=start, end=end, value=value[k],
                                                                  service=service, data_source=ds)

                    if created is True:
                        logger.info('Created DataPoint (start={}, end={}, value={}) '
                                    'for {}'.format(start, end, value, service))
                    else:
                        logger.warning('Duplicate datapoint found: (start={}, end={}, value={}) '
                                       'for {}. Not adding it.'.format(start, end, value, service))

                except ObjectDoesNotExist:
                    logger.warning('Service {} does not exist'.format(service_id))
                except KeyError:
                    # todo: {'AMS-IX_1_B': ('435469914691006', '740971501599081'), 'AMS-IX_1_A': ('765458816098426', '786666966235267')}
                    import pdb

                    pdb.set_trace()


class Command(BaseCommand):
    args = '<file file ...>'
    help = "Imports legacy SURFnet XML Reports"

    def handle(self, *args, **options):
        for filename in args:
            process_file(filename)