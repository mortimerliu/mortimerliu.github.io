from typing import Any, Optional, Tuple
import os
from datetime import datetime
import exchange_calendars as xcals

import pickle


def camel_to_snake(name: str) -> str:
    return "".join(
        ["_" + c.lower() if c.isupper() else c for c in name]
    ).lstrip("_")


def str2bytes(s: str) -> bytes:
    return s.encode("utf-8")


def bytes2str(b: bytes) -> str:
    return b.decode("utf-8")


def object2bytes(o: Any) -> bytes:
    return pickle.dumps(o)


def bytes2object(b: bytes) -> Any:
    return pickle.loads(b)


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S%Z"
DATETIME_FORMAT_NO_TZ = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


def datetime2str(dt: datetime, format=DATETIME_FORMAT) -> str:
    return dt.strftime(format)


def datetime2timestr(dt: datetime) -> str:
    return dt.strftime(TIME_FORMAT)


def datetime2datestr(dt: datetime) -> str:
    return dt.strftime(DATE_FORMAT)


def str2datetime(s: str, format=DATETIME_FORMAT) -> datetime:
    try:
        dt = datetime.strptime(s, format)
    except ValueError:
        dt = datetime.strptime(s, DATETIME_FORMAT_NO_TZ)
    return dt


def get_today() -> datetime:
    return datetime.today()


def makedirs(path: str):
    os.makedirs(path, exist_ok=True)


def is_core_market_minutes(dt: datetime) -> bool:
    """dt should be timezone aware"""
    assert dt.tzinfo is not None

    open_, close = get_market_open_close(dt)
    if open_ is None or close is None:
        return False
    return dt >= open_ and dt < close


def get_market_open_close(
    dt: Optional[datetime] = None,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Get the open and close times for the NASDAQ market on a given datetime.
    open is inclusive, close is exclusive.

    dt should be timezone aware. If dt is None, the current time is used.
    """
    if dt is None:
        dt = datetime.now().astimezone()  # local time, not UTC
    assert dt.tzinfo is not None
    nasdaq = xcals.get_calendar("NASDAQ")
    date = datetime2datestr(dt)
    if not nasdaq.is_session(date):
        return None, None
    open_ = nasdaq.schedule.at[date, "open"]
    close = nasdaq.schedule.at[date, "close"]
    return open_, close
