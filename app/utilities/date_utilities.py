import datetime

import isodate

from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)


def check_valid_iso8601_date(
    date: str | datetime.date | datetime.datetime,
) -> datetime.date | datetime.datetime | None:
    """
    Check if given date is a valid ISO 8601 date
    :param date: date to check
    :return: date if valid, None otherwise
    """
    if date is None:
        return None
    if isinstance(date, (datetime.date, datetime.datetime)):
        return date

    try:
        if isinstance(date, str):
            if "T" in date:
                return isodate.parse_datetime(date).replace(tzinfo=None)
            return isodate.parse_date(date)
        raise UnexpectedFormatException(
            "Date should be a string, datetime.date or datetime.datetime object"
        )
    except isodate.ISO8601Error as error:
        raise UnexpectedFormatException(
            f"Could not parse date {date} with error {error}"
        ) from error
