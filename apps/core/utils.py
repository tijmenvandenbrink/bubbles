import logging

logger = logging.getLogger(__name__)


def calculate_percentile():
    """ Calculate percentile on data set. """
    # todo: Create logic to calculate percentile
    pass


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