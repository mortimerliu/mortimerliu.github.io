from __future__ import annotations

import logging
from datetime import datetime
from datetime import timezone
from datetime import tzinfo


logger = logging.getLogger(__name__)


class UTCDateTime(datetime):
    """
    A datetime subclass that always represents time in UTC,
    that is, tzinfo is always timezone.utc

    If tzinfo is provided, the datetime is converted to UTC.
    If tzinfo is not provided, the datetime is assumed to be in UTC.
    """

    def __new__(
        cls,
        year: int,
        month: int,
        day: int,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None,
    ):
        dt = super().__new__(
            cls,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=timezone.utc,
        )
        if tzinfo is not None and not cls.is_utc_tzinfo(tzinfo):
            offset = tzinfo.utcoffset(None)
            dt -= offset
        return dt

    # TODO: refactor this out of the class
    @staticmethod
    def is_utc_tzinfo(tzinfo: tzinfo) -> bool:
        return tzinfo.utcoffset(None) == timezone.utc.utcoffset(None)

    @classmethod
    def now(cls, tz: tzinfo | None = None) -> UTCDateTime:
        if tz is not None:
            logger.warning("UTCDateTime is always in UTC, ignoring tz")
        return UTCDateTime.from_timezone_naive(datetime.utcnow())

    # TODO: refactor this out of the class
    @staticmethod
    def is_timezone_aware(dt: datetime) -> bool:
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

    @classmethod
    def from_timezone_naive(cls, dt: datetime) -> UTCDateTime:
        """For timezone naive datetime, assume it is in UTC."""
        if cls.is_timezone_aware(dt):
            raise ValueError(
                "datetime must be timezone naivel, "
                "use from_timezone_aware instead",
            )
        return UTCDateTime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=timezone.utc,
        )

    @classmethod
    def from_timezone_aware(cls, dt: datetime) -> UTCDateTime:
        """Convert timezone aware datetime to UTC."""
        if not cls.is_timezone_aware(dt):
            raise ValueError(
                "datetime must be timezone aware, "
                "use from_timezone_naive instead",
            )
        return UTCDateTime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=dt.tzinfo,
        )

    @classmethod
    def from_timestamp(cls, timestamp: float) -> UTCDateTime:
        dt = datetime.utcfromtimestamp(timestamp)
        return cls.from_timezone_naive(dt)

    @classmethod
    def from_utc(cls, dt: datetime) -> UTCDateTime:
        """Convert datetime that is already in UTC to UTCDateTime.
        The datetime may or may not be timezone aware.
        """
        if dt.tzinfo is not None and not cls.is_utc_tzinfo(dt.tzinfo):
            raise ValueError("datetime must be in UTC")
        if cls.is_timezone_aware(dt):
            return cls.from_timezone_aware(dt)
        return cls.from_timezone_naive(dt)

    @classmethod
    def from_isoformat(cls, s: str) -> UTCDateTime:
        dt = datetime.fromisoformat(s)
        if cls.is_timezone_aware(dt):
            return cls.from_timezone_aware(dt)
        return cls.from_timezone_naive(dt)

    def to_isoforamt(self) -> str:
        return self.isoformat()

    def to_timezone(self, tz: timezone | None = None) -> datetime:
        dt = datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo,
        )
        return dt.astimezone(tz)

    def __str__(self):
        return self.isoformat()

    def timestamp_ms(self) -> int:
        return int(self.timestamp() * 1000)


LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo
