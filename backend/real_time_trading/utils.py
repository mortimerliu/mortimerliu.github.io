from __future__ import annotations

import os
import pickle
from datetime import datetime
from datetime import timezone
from typing import Any

import exchange_calendars as xcals
from real_time_trading.objects.utc_datetime import UTCDateTime


def camel_to_snake(name: str) -> str:
    return "".join(
        ["_" + c.lower() if c.isupper() else c for c in name],
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
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


def datetime2str(dt: datetime, format=DATETIME_FORMAT) -> str:
    return dt.strftime(format)


def datetime2datestr(dt: datetime, format=DATE_FORMAT) -> str:
    return dt.strftime(format)


def datetime2timestr(dt: datetime, format=TIME_FORMAT) -> str:
    return dt.strftime(format)


def str2datetime(s: str, format=DATETIME_FORMAT) -> datetime:
    return datetime.strptime(s, format)


def get_today() -> datetime:
    return datetime.today()


def get_utcnow() -> datetime:
    """Get the current time in UTC, timezone aware"""
    return datetime.now(timezone.utc)


def makedirs(path: str):
    os.makedirs(path, exist_ok=True)


def is_core_market_minutes(dt: UTCDateTime) -> bool:
    """dt should be timezone aware"""
    assert dt.tzinfo is not None

    open_, close = get_market_open_close(dt)
    if open_ is None or close is None:
        return False
    return dt >= open_ and dt < close


def get_market_open_close(
    dt: UTCDateTime | None = None,
) -> tuple[UTCDateTime | None, UTCDateTime | None]:
    """Get the open and close times for the NASDAQ market on a given datetime.
    open is inclusive, close is exclusive.

    dt should be timezone aware. If dt is None, the current time is used.
    """
    if dt is None:
        dt = UTCDateTime.now()  # local time, not UTC

    nasdaq = xcals.get_calendar("NASDAQ")
    date = datetime2datestr(dt)
    if not nasdaq.is_session(date):
        return None, None
    open_ = nasdaq.session_open(date)
    close = nasdaq.session_close(date)
    return UTCDateTime.from_utc(open_), UTCDateTime.from_utc(close)


def get_local_now() -> datetime:
    """get the current time in local timezone"""
    return datetime.now().astimezone()
