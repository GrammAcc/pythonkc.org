"""Date/Time helper functions."""

__all__ = [
    "now",
    "timestamp",
    "today",
]

import datetime
import math
import time

from pykc.constants import TIMEZONE


def now() -> datetime.datetime:
    """Return the current time in UTC."""

    return datetime.datetime.now(datetime.UTC)


def today() -> datetime.date:
    """Today's date in US Central time."""

    return datetime.datetime.now(TIMEZONE).date()


def timestamp() -> int:
    """Return the current unix timestamp as an integer not a float."""

    return math.floor(time.time())
