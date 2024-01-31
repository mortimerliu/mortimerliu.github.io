from typing import Any
from datetime import datetime
from ib_insync import Ticker

import utils


class RawTicker:
    @staticmethod
    def from_message(message: dict[str, Any]) -> "RawTicker":
        return RawTicker(
            symbol=message["symbol"],
            last=message["last"],
            bid=message["bid"],
            ask=message["ask"],
            time=utils.str2datetime(message["time"]),
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
            time=ticker.time,
        )

    def __init__(
        self, symbol: str, last: float, bid: float, ask: float, time: datetime
    ):
        self.symbol = symbol
        self.last = last
        self.bid = bid
        self.ask = ask
        self.time = time

    def to_message(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "last": self.last,
            "bid": self.bid,
            "ask": self.ask,
            "time": utils.datetime2str(self.time),
        }
