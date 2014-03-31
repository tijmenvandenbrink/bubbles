import logging
from datetime import datetime

from pandas import DataFrame, period_range
import numpy as np
from django.utils.timezone import utc

logger = logging.getLogger(__name__)


def consolidate():
    """
    """
    # todo: Create consolidate function
    pass


def get_derived_value(data, interval):
    """ Return the start, end and derived value over a list of timestamp/value pairs:

        :param data: list of tuples [(timestamp, value), ..]
        :type data: list
        :param interval: interval rate in seconds of samples
        :type interval: integer
        :returns: start, end, value
    """
    from operator import itemgetter
    from datetime import timedelta

    from django.utils.timezone import utc

    if len(data) <= 1:
        return False

    # Find first and last sample
    start = min(data, key=itemgetter(1))[0].replace(tzinfo=utc)
    end = max(data, key=itemgetter(1))[0].replace(tzinfo=utc) + timedelta(0, interval)

    # Check if values are always incrementing
    data.sort(reverse=True)
    t1 = data.pop()
    value = 0
    start_value = t1[1]
    while not len(data) == 0:
        t2 = data.pop()
        if not t1[1] <= t2[1]:
            # Counter wrap. Discard the sample and reset start_value
            logger.warning('Found a counter wrap. {0} <= {1}'.format(t1[1], t2[1]))
            value += t1[1] - start_value
            start_value = t2[1]

        if not (t2[0] - t1[0]) == timedelta(0, interval):
            logger.warning('Found non-contiguous samples - {0} - {1}'.format(t1[0], t2[0]))

        t1 = t2

    value += t2[1] - start_value

    logger.debug('Returning derived_value: start={0}, end={1}, value={2}'.format(start, end, value))
    return start, end, value


def mkdate(datestring):
    """ Return a datetime object from string

        :param datestring: date string in the form of YYYY-MM-DD
        :type datestring: string
        :returns: datetime object
    """
    from datetime import datetime
    from django.utils.timezone import utc
    import re

    if re.match('\d{4}-\d{1,2}-{1,2}', datestring):
        return datetime.strptime(datestring, '%Y-%m-%d').replace(tzinfo=utc)
    elif re.match('\d{4}-\d{1,2}', datestring):
        return datetime.strptime(datestring, '%Y-%m').replace(tzinfo=utc)


def overlap(l1, l2):
    """
        Look for overlapping intervals between two lists.
        Each list consist of lists with a start and end datetime objects:
                 [(start, end), (start, end), ....]
        Any or both lists may be empty.

        A1       e1[0]------e1[1]                               e1[0] <= e2[0] and e1[1] <= e2[0]
                                    e2[0]------e2[1]
                                                                      OR
        A2                          e1[0]------e1[1]            e1[0] >= e2[1] and e1[1] >= e2[1]
                 e2[0]------e2[1]


        B1       e1[0]------e1[1]                               e1[0] <= e2[0] and e1[1] <= e2[1]
                        e2[0]------e2[1]
                                                                      OR
        B2              e1[0]------e1[1]                        e1[0] >= e2[0] and e1[1] >= e2[1]
                 e2[0]------e2[1]


        C1       e1[0]--------------------e1[1]                 e1[0] <= e2[0] and e1[1] >= e2[1]
                       e2[0]------e2[1]
                                                                         OR
        C2              e1[0]-----e1[1]                         e1[0] >= e2[0] and e1[1] <= e2[1]
                   e2[0]---------------------e2[1]

        Situation A1 -> No overlap
        Situation A2 -> No overlap

        Situation B1 -> start = e2[0], end = e1[1]
        Situation B2 -> start = e1[0], end = e2[1]

        Situation C1 -> start = e2[0], end = e2[1]
        Situation C2 -> start = e1[0], end = e1[1]

        :param l1: List of start, end tuples. [(start, end), (start, end), ....]
        :type l1: list
        :param l2: List of start, end tuples. [(start, end), (start, end), ....]
        :type l2: list
        :returns: list of start, end tuples. [(start, end), (start, end), ....]
    """
    result = []
    for e1 in l1:
        for e2 in l2:
            if (e1[0] <= e2[0] and e1[1] <= e2[0]) or (e1[0] >= e2[1] and e1[1] >= e2[1]):  #A1 and A2
                continue
            elif e1[0] <= e2[0] and e1[1] <= e2[1]:                                         #B1
                start = e2[0]
                end = e1[1]
            elif e1[0] >= e2[0] and e1[1] >= e2[1]:                                         #B2
                start = e1[0]
                end = e2[1]
            elif e1[0] <= e2[0] and e1[1] >= e2[1]:                                         #C1
                start = e2[0]
                end = e2[1]
            elif e1[0] >= e2[0] and e1[1] <= e2[1]:                                         #C2
                start = e1[0]
                end = e1[1]
            else:
                return result

            result.append((start, end))

    return result


def calculate_availability(start, end, duration):
    """
        Return availability percentage
        start, end are datetime objects and represents the period
        over which the availability should be calculated.
        duration is a timedelta object
    """
    total = end - start
    result = (1.0 - (duration.total_seconds() / total.total_seconds())) * 100

    return result


def update_obj(obj, **kwargs):
    """ Updates an object with kwargs and returns the object

    :param obj: Object
    :type obj: Object
    :return: Object
    """
    for k, v in kwargs.items():
        if not getattr(obj, k) == v:
            logger.info('action="Object update", status="OK", object_id="{obj.id}", object="{obj}", '
                        'attribute="{attribute}", oldvalue="{oldvalue}", '
                        'newvalue="{newvalue}"'.format(obj=obj, attribute=k, oldvalue=getattr(obj, k), newvalue=v))
            setattr(obj, k, v)
    obj.save()
    return obj


def create_multibarchart(obj, datasources, freq='D'):
    """
        Returns a multibarchart
    """
    start_time = datetime.utcnow().replace(tzinfo=utc)
    end_time = datetime.min.replace(tzinfo=utc)

    tooltip_date = "%d %b %Y"
    extra_serie = {"tooltip": {"y_start": "", "y_end": ""},
                   "date_format": tooltip_date}

    data = {}
    for ds in datasources:
        dps = obj.get_datapoints(ds, recursive=True)
        if not dps.count():
            continue
        df = DataFrame(list(dps.values('start', 'value')))
        df.set_index('start', inplace=True)
        ps = df.to_period(freq=freq).groupby(level=0).sum()

        if dps.order_by('start').first().start < start_time:
            start_time = dps.order_by('start').first().start

        if dps.order_by('end').last().end > end_time:
            end_time = dps.order_by('end').last().start

        data[ds] = ps

    prng = period_range(start=start_time.replace(hour=0, minute=0, second=0),
                        end=end_time.replace(hour=0, minute=0, second=0))
    ps_total = DataFrame(index=prng)
    columns = []
    for ds, ps in data.items():
        columns.append(ds.name)
        ps_total = ps_total.join(ps, lsuffix='_left', rsuffix='_right')
        ps_total.columns = columns

    ps_total = ps_total.reindex(prng).fillna(0)
    ps_total = ps_total.applymap(lambda x: x/1024**3)

    chartdata = {}
    i = 0
    for ds in ps_total.columns:
        i += 1
        chartdata['name{}'.format(i)] = ds
        chartdata['y{}'.format(i)] = [float(x) for x in list(ps_total[ds].values)]
        chartdata['extra{}'.format(i)] = extra_serie

    chartdata['x'] = [str(x / 10**6) for x in list(ps_total.index.to_datetime().astype(np.int64))]

    data = {
        'charttype': 'multiBarChart',
        'chartdata_with_date': chartdata,
        'chartcontainer_with_date': 'date_multibarchart_container',
        'extra_with_date': {
            'name': 'date_multibarchart_container',
            'x_is_date': True,
            'x_axis_format': '%d %b %Y',
            'tag_script_js': True,
            'jquery_on_ready': True,
        },
    }

    return data