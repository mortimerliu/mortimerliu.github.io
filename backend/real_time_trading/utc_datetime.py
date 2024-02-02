from typing import Optional
from datetime import datetime, timezone


class UTCDateTime(datetime):
    """
    A datetime subclass that always represents time in UTC,
    that is, tzinfo is always timezone.utc
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
        if tzinfo is not None and tzinfo is not timezone.utc:
            offset = tzinfo.utcoffset(None)
            dt -= offset
        return dt

    @staticmethod
    def now() -> "UTCDateTime":
        return UTCDateTime.from_timezone_naive(datetime.utcnow())

    @staticmethod
    def is_timezone_aware(dt: datetime) -> bool:
        return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

    @classmethod
    def from_timezone_naive(cls, dt: datetime) -> "UTCDateTime":
        if cls.is_timezone_aware(dt):
            raise ValueError(
                "datetime must be timezone naivel, use from_timezone_aware instead"
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
    def from_timezone_aware(cls, dt: datetime) -> "UTCDateTime":
        if not cls.is_timezone_aware(dt):
            raise ValueError(
                "datetime must be timezone aware, use from_timezone_naive instead"
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
    def from_isoformat(cls, s: str) -> "UTCDateTime":
        dt = datetime.fromisoformat(s)
        if cls.is_timezone_aware(dt):
            return cls.from_timezone_aware(dt)
        return cls.from_timezone_naive(dt)

    def to_isoforamt(self) -> str:
        return self.isoformat()

    def to_timezone(self, tz: timezone) -> datetime:
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

    def to_datestr(self) -> str:
        return self.strftime("%Y-%m-%d")
