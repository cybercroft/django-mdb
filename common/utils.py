from django.utils import timezone as tz
from django.conf import settings


def format_date_to_str(date, format="%Y-%m-%d", localize=True):
    _date = tz.localtime(date) if localize else date
    return f"{_date.strftime(format)}"


def date_to_str(date, localize=True):
    return format_date_to_str(date=date, format=settings.DATE_FORMAT, localize=localize)


def datetime_to_str(date, localize=True):
    return format_date_to_str(date=date, format=settings.DATETIME_FORMAT, localize=localize)
