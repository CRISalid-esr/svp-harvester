import datetime
import isodate

from app.harvesters.exceptions.unexpected_format_exception import (
    UnexpectedFormatException,
)


def check_valid_iso8601_date(
    date: str | datetime.date | datetime.datetime,
) -> datetime.date | None:
    """
    Parse a date-like value and normalize it to datetime.date.
    Accepts ISO-8601 dates, ISO-8601 datetimes, and legacy SQL-style datetimes.
    """
    if date is None:
        return None

    if isinstance(date, datetime.datetime):
        return date.date()

    if isinstance(date, datetime.date):
        return date

    if not isinstance(date, str):
        raise UnexpectedFormatException(
            "Date should be a string, datetime.date or datetime.datetime object"
        )

    # 1) Strict ISO-8601 datetime
    try:
        dt = isodate.parse_datetime(date).replace(tzinfo=None)
        return dt.date()
    except Exception:
        pass

    # 2) Strict ISO-8601 date
    try:
        return isodate.parse_date(date)
    except Exception:
        pass

    # 3) Legacy / SQL-like datetime
    try:
        return datetime.datetime.fromisoformat(date).date()
    except ValueError:
        pass

    raise UnexpectedFormatException(f"Unsupported date format: {date}")
