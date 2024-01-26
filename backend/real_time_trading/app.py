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
from ib_insync import IB, util, Ticker
from ib_insync.contract import Stock
import logging

util.logToConsole(logging.DEBUG)

ib = IB()
ib.connect("3.17.188.231", 7496, clientId=1)

TICKER_QUEUE = deque()


def camel_to_snake(name: str) -> str:
    return "".join(
        ["_" + c.lower() if c.isupper() else c for c in name]
    ).lstrip("_")


@dataclass
class IntradayRecord(ABC):
    NO_VALUE: ClassVar[float] = -1.0  # TODO: revisit, change to np.nan?

    contract: Optional[Stock]
    time: datetime = datetime.now()
    price: float = NO_VALUE
    count: int = -1
    _initial_time: datetime = datetime.now()
    _initial_price: float = NO_VALUE
    last_price: float = NO_VALUE

    @property
    def gap(self) -> float:
        if self._initial_price == self.NO_VALUE:
            raise ValueError("initial price is not set")
        return (self.price - self._initial_price) / self._initial_price

    def _time_str(self) -> str:
        return self.time.astimezone().strftime("%H:%M:%S")

    @abstractmethod
    def should_update(self, ticker: Ticker) -> bool:
        raise NotImplementedError

    def update(self, ticker: Ticker) -> bool:
        assert ticker.time is not None, "ticker.time is None"
        if self._initial_price == self.NO_VALUE:
            self._initial_price = ticker.last
            self._initial_time = ticker.time
        if self.should_update(ticker):
            self.time = ticker.time
            self.price = ticker.last
            self.count += 1
            return True
        return False

    def to_message(self) -> dict[str, Any]:
        return {
            "type": camel_to_snake(self.__class__.__name__),
            "data": {
                "time": self._time_str(),
                "symbol": self.contract.symbol,
                "price": self.price,
                "gap": self.gap,
                "cnt": self.count,
            },
        }


@dataclass
class IntradayHigh(IntradayRecord):
    def should_update(self, ticker: Ticker) -> bool:
        return self.price == self.NO_VALUE or ticker.last > self.price


@dataclass
class IntradayLow(IntradayRecord):
    def should_update(self, ticker: Ticker) -> bool:
        return self.price == self.NO_VALUE or ticker.last < self.price


INTRADAY_HIGHS = {}
INTRADAY_LOWS = {}

symbols = [
    {
        "symbol": "AAPL",
        "exchange": "SMART",
        "currency": "USD",
    },
    {
        "symbol": "AMZN",
        "exchange": "SMART",
        "currency": "USD",
    },
    {
        "symbol": "GOOGL",
        "exchange": "SMART",
        "currency": "USD",
    },
    {
        "symbol": "NVDA",
        "exchange": "SMART",
        "currency": "USD",
    },
    {
        "symbol": "MSFT",
        "exchange": "SMART",
        "currency": "USD",
    },
]

contracts = [Stock(**stk) for stk in symbols]
for contract in contracts:
    INTRADAY_HIGHS[contract.symbol] = IntradayHigh(contract=contract)
    INTRADAY_LOWS[contract.symbol] = IntradayLow(contract=contract)
ib.qualifyContracts(*contracts)


async def process(websocket):
    while True:
        if TICKER_QUEUE:
            ticker: Ticker = TICKER_QUEUE.popleft()
            intraday_high = INTRADAY_HIGHS[ticker.contract.symbol]
            high_updated = intraday_high.update(ticker)
            if high_updated:
                await websocket.send(json.dumps(intraday_high.to_message()))

            intraday_low = INTRADAY_LOWS[ticker.contract.symbol]
            low_updated = intraday_low.update(ticker)
            if low_updated:
                await websocket.send(json.dumps(intraday_low.to_message()))
        else:
            await asyncio.sleep(0.1)


async def handler(websocket):
    # async for message in websocket:
    #     print(message)

    for contract in contracts:
        ib.reqMktData(contract, "", False, False, [])

    def onPendingTickers(tickers):
        for t in tickers:
            TICKER_QUEUE.append(t)

    ib.pendingTickersEvent += onPendingTickers

    await process(websocket)


async def main():
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", 5001))
    async with websockets.serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
