import nest_asyncio

nest_asyncio.apply()


from abc import ABC, abstractmethod
import pickle
import logging
from typing import List, Set, Callable
from eventkit import Event
from ib_insync import IB, util, Ticker
from ib_insync.contract import Stock

import constants
from handlers import Handler, RawTickerKafkaHandler, RawTickerFileHandler

logging.getLogger("kafka").setLevel(logging.INFO)

util.logToConsole(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler("ibapp.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class AsyncIBApp:
    """Wrapper class for ib_insync.IB."""

    def __init__(self, host: str, port: int, client_id: int):
        self.host = host
        self.port = port
        self.client_id = client_id
        self._ib = IB()
        # self.market_data_callbacks: List[Handler] = []

    def connect(self):
        self._ib.connect(
            host=self.host, port=self.port, clientId=self.client_id
        )

    def disconnect(self):
        self._ib.disconnect()

    def request_market_data(
        self, contracts: List[Stock], callbacks: List[Handler]
    ):
        for contract in contracts:
            self._ib.reqMktData(
                contract=contract,
                genericTickList="",
                snapshot=False,
                regulatorySnapshot=False,
                mktDataOptions=[],
            )

        for callback in callbacks:
            self._ib.pendingTickersEvent += callback
            # self.market_data_callbacks.append(callback)

    def run(self):
        self._ib.run()

    def register_event_handler(self, event_name: str, handler: Callable):
        event: Event = getattr(self._ib, event_name)
        event += handler

    def sleep(self, seconds: int):
        self._ib.sleep(seconds)


if __name__ == "__main__":
    CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]
    raw_ticker_kafka_handler = RawTickerKafkaHandler(
        topic=constants.RAW_TICKER_EVENT
    )
    raw_ticker_file_handler = RawTickerFileHandler(directory="data/raw_ticker")
    HANDLERS: List[Handler] = [
        raw_ticker_kafka_handler,
        raw_ticker_file_handler,
    ]

    def on_connected():
        logger.info("ibapi connected to tws")
        logger.info("requesting market data...")
        ibapp.request_market_data(contracts=CONTRACTS, callbacks=HANDLERS)

    def on_disconnected():
        logger.warning("ibapi disconnected from tws, sleeping for 5s...")
        ibapp.sleep(5)
        logger.warning("reconnecting...")
        ibapp.connect()

    ibapp = AsyncIBApp(host="localhost", port=7496, client_id=1)
    ibapp.register_event_handler("connectedEvent", on_connected)
    ibapp.register_event_handler("disconnectedEvent", on_disconnected)

    ibapp.connect()
    ibapp.run()
