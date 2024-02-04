from typing import Any
from datetime import datetime
from ib_insync import Ticker
from dataclasses import dataclass

from real_time_trading.objects.utc_datetime import UTCDateTime
import utils


@dataclass
class RawTicker:
    symbol: str
    last: float
    bid: float
    ask: float
    time: UTCDateTime

    def to_message(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "last": self.last,
            "bid": self.bid,
            "ask": self.ask,
            "time": self.time.to_isoforamt(),
        }

    @staticmethod
    def from_message(message: dict[str, Any]) -> "RawTicker":
        return RawTicker(
            symbol=message["symbol"],
            last=message["last"],
            bid=message["bid"],
            ask=message["ask"],
            time=UTCDateTime.from_isoformat(message["time"]),
        )

    @staticmethod
    def from_ticker(ticker: Ticker) -> "RawTicker":
        assert ticker.contract is not None
        assert ticker.time is not None
        return RawTicker(
            symbol=ticker.contract.symbol,
            last=ticker.last,
            bid=ticker.bid,
            ask=ticker.ask,
            time=UTCDateTime.from_utc(ticker.time),
        )
