from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import constants
import nest_asyncio
from ib_insync.contract import Stock
from kafka import KafkaProducer
from real_time_trading.objects.raw_ticker import RawTicker
from real_time_trading.objects.utc_datetime import UTCDateTime


nest_asyncio.apply()
logger = logging.getLogger(__name__)


@dataclass
class IntradayEvent:
    time: UTCDateTime
    symbol: str
    price: float
    gap: float
    count: int

    @staticmethod
    def from_event_message(message: dict[str, Any]) -> IntradayEvent:
        return IntradayEvent(
            time=UTCDateTime.from_isoformat(message["time"]),
            symbol=message["symbol"],
            price=message["price"],
            gap=message.get("gap", -1.0),
            count=message.get("count", -1),
        )

    def to_event_message(self, local_time: bool = False) -> dict[str, Any]:
        if local_time:
            time_str = self.time.to_timezone().isoformat()
        else:
            time_str = self.time.to_isoforamt()
        return {
            "time": time_str,
            "symbol": self.symbol,
            "price": self.price,
            "gap": self.gap,
            "count": self.count,
        }


class IntradayTicker:
    NO_VALUE: float = -1.0  # TODO: revisit, change to np.nan?

    def __init__(
        self,
        contract: Stock,
        kafka_producer: KafkaProducer,
        intraday_high_threshold: float = 0.0,
        intraday_low_threshold: float = 0.0,
    ):
        assert contract.symbol is not None
        self.contract = contract
        self.kafka_producer = kafka_producer
        self.intraday_high_threshold = intraday_high_threshold
        self.intraday_low_threshold = intraday_low_threshold
        self.reset()

    # @property
    # def last_price(self) -> float:
    #     if not self.hasData():
    #         raise ValueError("No data")
    #     return self.tickers[-1].last

    # @property
    # def last_time(self) -> datetime:
    #     if not self.hasData():
    #         raise ValueError("No data")
    #     assert self.tickers[-1].time is not None
    #     return self.tickers[-1].time

    def reset(self):
        # self.tickers: list[RawTicker] = []
        self.first_price: float = self.NO_VALUE
        self.last_price: float = self.NO_VALUE

        self.intraday_high: float = self.NO_VALUE
        self.intrady_low: float = self.NO_VALUE

        self.intraday_highs: list[IntradayEvent] = []
        self.intraday_lows: list[IntradayEvent] = []

    def hasData(self) -> bool:
        # return len(self.tickers) > 0
        return self.first_price != self.NO_VALUE

    def _get_gap(self, price) -> float:
        if not self.hasData():
            logger.warning("Ticker %s has no data", self.contract.symbol)
            return 0.0
        return (price - self.first_price) / self.first_price

    @property
    def gap(self) -> float:
        return self._get_gap(self.last_price)

    def is_new_high(self, ticker: RawTicker) -> bool:
        if not self.hasData():
            return False
        return ticker.last > self.intraday_high * (
            1 + self.intraday_high_threshold
        )

    def is_new_low(self, ticker: RawTicker) -> bool:
        if not self.hasData():
            return False
        return ticker.last < self.intraday_low * (
            1 - self.intraday_low_threshold
        )

    def update(self, raw_ticker: RawTicker) -> bool:
        assert raw_ticker.symbol == self.contract.symbol
        update_flag = False

        if self.is_new_high(raw_ticker):
            intraday_high = IntradayEvent(
                time=raw_ticker.time,
                symbol=raw_ticker.symbol,
                price=raw_ticker.last,
                gap=self._get_gap(raw_ticker.last),
                count=len(self.intraday_highs) + 1,
            )
            self.intraday_highs.append(intraday_high)
            self.kafka_producer.send(
                constants.INTRADAY_HIGH_EVENT,
                key=self.contract.symbol,
                value=intraday_high.to_event_message(),
                timestamp_ms=raw_ticker.time.timestamp_ms(),
            )
            logger.info("sending intraday high event")
            self.intraday_high = raw_ticker.last
            update_flag = True
        elif self.is_new_low(raw_ticker):
            intraday_low = IntradayEvent(
                time=raw_ticker.time,
                symbol=raw_ticker.symbol,
                price=raw_ticker.last,
                gap=self._get_gap(raw_ticker.last),
                count=len(self.intraday_lows) + 1,
            )
            self.intraday_lows.append(intraday_low)
            self.kafka_producer.send(
                constants.INTRADAY_LOW_EVENT,
                key=self.contract.symbol,
                value=intraday_low.to_event_message(),
                timestamp_ms=raw_ticker.time.timestamp_ms(),
            )
            logger.info("sending intraday low event")
            self.intraday_low = raw_ticker.last
            update_flag = True

        # self.tickers.append(ticker)
        self.last_price = raw_ticker.last
        if not self.hasData():
            self.first_price = raw_ticker.last
            self.intraday_high = raw_ticker.last
            self.intraday_low = raw_ticker.last

        return update_flag
