import datetime

from django import template
from django.conf import settings

import pytz


register = template.Library()


def pretty_timestamp(timestamp):
    local_tz = pytz.timezone(settings.TIME_ZONE)

    try:
        ts = float(timestamp)
    except ValueError:
        return None

    # Specify Format here
    # return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))
    return local_tz.localize(datetime.datetime.fromtimestamp(ts))

register.filter(pretty_timestamp)
