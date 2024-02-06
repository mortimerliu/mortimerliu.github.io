from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
from real_time_trading.objects.utc_datetime import UTCDateTime

UTC_UTCOFFSET = timedelta(hours=0)


def test_utc_datetime():
    dt = UTCDateTime(year=2021, month=1, day=1, hour=3, minute=30)
    assert isinstance(dt, UTCDateTime)
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == UTC_UTCOFFSET
    assert dt.year == 2021
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 3
    assert dt.minute == 30
    assert dt.second == 0

    dt = UTCDateTime(2021, 1, 1, 15, 30, tzinfo=timezone(timedelta(hours=8)))
    assert isinstance(dt, UTCDateTime)
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == UTC_UTCOFFSET
    assert dt.year == 2021
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 7
    assert dt.minute == 30
    assert dt.second == 0


def test_utc_datetime_is_timezone_aware():
    dt = UTCDateTime.now()
    assert UTCDateTime.is_timezone_aware(dt)

    dt = datetime.now()
    assert not UTCDateTime.is_timezone_aware(dt)

    dt = dt.astimezone()
    assert UTCDateTime.is_timezone_aware(dt)


def test_utc_datetime_from_timezone_naive():
    dt = datetime(2021, 1, 1, 3, 30)
    utc_dt = UTCDateTime.from_timezone_naive(dt)
    assert isinstance(utc_dt, UTCDateTime)
    assert utc_dt.tzinfo is not None
    assert utc_dt.tzinfo.utcoffset(utc_dt) == UTC_UTCOFFSET
    assert utc_dt.year == dt.year
    assert utc_dt.month == dt.month
    assert utc_dt.day == dt.day
    assert utc_dt.hour == dt.hour
    assert utc_dt.minute == dt.minute
    assert utc_dt.second == dt.second

    with pytest.raises(ValueError):
        dt = datetime(2021, 1, 1, 3, 30, tzinfo=timezone.utc)
        UTCDateTime.from_timezone_naive(dt)


def test_utc_datetime_from_timezone_aware():
    dt = datetime(2021, 1, 1, 15, 30, tzinfo=timezone(timedelta(hours=8)))
    utc_dt = UTCDateTime.from_timezone_aware(dt)
    assert isinstance(utc_dt, UTCDateTime)
    assert utc_dt.tzinfo is not None
    assert utc_dt.tzinfo.utcoffset(utc_dt) == UTC_UTCOFFSET
    assert utc_dt.year == dt.year
    assert utc_dt.month == dt.month
    assert utc_dt.day == dt.day
    assert utc_dt.hour == dt.hour - 8
    assert utc_dt.minute == dt.minute
    assert utc_dt.second == dt.second

    with pytest.raises(ValueError):
        dt = datetime(2021, 1, 1, 3, 30)
        UTCDateTime.from_timezone_aware(dt)


@pytest.mark.parametrize(
    "year, month, day, hour, minute, tzinfo",
    [
        (2021, 1, 1, 3, 30, timezone.utc),
        (2021, 1, 1, 15, 30, None),
        (2021, 1, 1, 15, 30, timezone(timedelta(hours=8))),
    ],
)
def test_utc_datetime_from_isoformat(year, month, day, hour, minute, tzinfo):
    dt = datetime(year, month, day, hour, minute, tzinfo=tzinfo)
    iso_str = dt.isoformat()
    utc_dt = UTCDateTime.from_isoformat(iso_str)
    assert isinstance(utc_dt, UTCDateTime)
    assert utc_dt.tzinfo is not None
    assert utc_dt.tzinfo.utcoffset(utc_dt) == UTC_UTCOFFSET


def test_utc_datetime_to_timezone():
    utc_dt = UTCDateTime(2021, 1, 1, 3, 30)
    dt = utc_dt.to_timezone(timezone(timedelta(hours=8)))
    assert isinstance(dt, datetime)
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == timedelta(hours=8)
    assert dt.year == 2021
    assert dt.month == 1
    assert dt.day == 1
    assert dt.hour == 11
    assert dt.minute == 30
    assert dt.second == 0
