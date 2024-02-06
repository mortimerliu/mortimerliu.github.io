from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from real_time_trading.objects.intraday_ticker import IntradayTicker
from real_time_trading.objects.utc_datetime import UTCDateTime


@dataclass
class TopSymbol:
    symbol: str
    last: float
    gap: float

    def to_event_message(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "last": self.last,
            "gap": self.gap,
        }

    @staticmethod
    def from_event_message(message: dict[str, Any]) -> TopSymbol:
        return TopSymbol(
            symbol=message["symbol"],
            last=message["last"],
            gap=message["gap"],
        )

    @staticmethod
    def from_ticker(ticker: IntradayTicker) -> TopSymbol:
        return TopSymbol(
            symbol=ticker.contract.symbol,
            last=ticker.last_price,
            gap=ticker.gap,
        )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TopSymbol):
            return False
        return (
            self.symbol == value.symbol
            and self.last == value.last
            and self.gap == value.gap
        )


class TopNSymbols:
    def __init__(self, time: UTCDateTime, top_symbols: list[TopSymbol]):
        self.time = time
        self.symbols = top_symbols

    def to_message(self) -> dict[str, Any]:
        return {
            "time": self.time.to_isoforamt(),
            "data": self.to_message_only_data(),
        }

    def to_message_only_data(self) -> list[dict[str, Any]]:
        return [s.to_event_message() for s in self.symbols]

    @staticmethod
    def from_message(message: dict[str, Any]) -> TopNSymbols:
        return TopNSymbols(
            time=UTCDateTime.from_isoformat(message["time"]),
            top_symbols=[
                TopSymbol.from_event_message(m) for m in message["data"]
            ],
        )

    @staticmethod
    def from_tickers(
        time: UTCDateTime,
        tickers: list[IntradayTicker],
    ) -> TopNSymbols:
        return TopNSymbols(time, [TopSymbol.from_ticker(t) for t in tickers])

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, TopNSymbols):
            return False
        return self.symbols == value.symbols
