from typing import Any
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


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"


def datetime2str(dt: datetime, format=DATETIME_FORMAT) -> str:
    return dt.strftime(format)


def datetime2timestr(dt: datetime) -> str:
    return dt.strftime(TIME_FORMAT)


def datetime2datestr(dt: datetime) -> str:
    return dt.strftime(DATE_FORMAT)


def str2datetime(s: str, format=DATETIME_FORMAT) -> datetime:
    return datetime.strptime(s, format)


def get_today() -> datetime:
    return datetime.today()


def makedirs(path: str):
    os.makedirs(path, exist_ok=True)


def is_core_market_minutes(dt: datetime) -> bool:
    nasdaq = xcals.get_calendar("NASDAQ")
    date = datetime2datestr(dt)
    if not nasdaq.is_session(date):
        return False
    open_ = nasdaq.schedule.at[date, "open"]
    close = nasdaq.schedule.at[date, "close"]

    return dt >= open_ and dt < close
