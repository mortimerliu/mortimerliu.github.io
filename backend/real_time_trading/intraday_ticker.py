import nest_asyncio

nest_asyncio.apply()

from typing import Any, ClassVar, Optional
from abc import ABC, abstractmethod

import os
import signal
import json
import time
import threading
import asyncio
import websockets
from datetime import datetime
from collections import deque
from collections import defaultdict
from dataclasses import dataclass
from ib_insync import Ticker
from ib_insync.contract import Stock

from kafka import KafkaConsumer, KafkaProducer
from utc_datetime import UTCDateTime

from raw_ticker import RawTicker
import utils


@dataclass
class IntradayEvent:
    time: UTCDateTime
    symbol: str
    price: float
    gap: float
    count: int

    @staticmethod
    def from_event_message(message: dict[str, Any]) -> "IntradayEvent":
        return IntradayEvent(
            time=UTCDateTime.from_isoformat(message["time"]),
            symbol=message["symbol"],
            price=message["price"],
            gap=message.get("gap", -1.0),
            count=message.get("count", -1),
        )

    def to_event_message(self) -> dict[str, Any]:
        return {
            "time": self.time.to_isoforamt(),
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
            raise ValueError("No data")
        return (price - self.first_price) / self.first_price

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

    def update(self, raw_ticker: RawTicker):
        assert raw_ticker.symbol == self.contract.symbol
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
                "intraday_high",
                key=self.contract.symbol,
                value=intraday_high.to_event_message(),
            )
            self.intraday_high = raw_ticker.last
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
                "intraday_low",
                key=self.contract.symbol,
                value=intraday_low.to_event_message(),
            )
            self.intraday_low = raw_ticker.last

        if not self.hasData():
            self.intraday_high = raw_ticker.last
            self.intraday_low = raw_ticker.last

        # self.tickers.append(ticker)
        self.last_price = raw_ticker.last
        if not self.hasData():
            self.first_price = raw_ticker.last
