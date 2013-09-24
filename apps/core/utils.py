import logging

logger = logging.getLogger(__name__)


def calculate_percentile():
    """ Calculate percentile on data set. """
    # todo Create logic to calculate percentile
    pass


def consolidate():
    """
    """
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