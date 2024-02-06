from __future__ import annotations

import logging
from typing import Callable

import constants
import nest_asyncio
from eventkit import Event
from handlers import Handler
from handlers import RawTickerFileHandler
from handlers import RawTickerKafkaHandler
from ib_insync import IB
from ib_insync import util
from ib_insync.contract import Stock


nest_asyncio.apply()
util.logToConsole(logging.INFO)
logging.getLogger("kafka").setLevel(logging.INFO)


formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(constants.IBAPP_LOG_FILE)
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
            host=self.host,
            port=self.port,
            clientId=self.client_id,
        )

    def disconnect(self):
        self._ib.disconnect()

    def request_market_data(
        self,
        contracts: list[Stock],
        callbacks: list[Handler],
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
        event: Event = getattr(self._ib, event_name)  # NOSONAR
        event += handler

    def sleep(self, seconds: int):
        self._ib.sleep(seconds)

    def is_connected(self):
        return self._ib.isConnected()


if __name__ == "__main__":
    CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]
    raw_ticker_kafka_handler = RawTickerKafkaHandler(
        topic=constants.RAW_TICKER_EVENT,
    )
    raw_ticker_file_handler = RawTickerFileHandler(directory="data/raw_ticker")
    HANDLERS: list[Handler] = [
        raw_ticker_kafka_handler,
        raw_ticker_file_handler,
    ]

    def on_connected():
        logger.info("ibapi connected to tws")
        logger.info("requesting market data...")
        ibapp.request_market_data(contracts=CONTRACTS, callbacks=HANDLERS)

    def on_disconnected():
        logger.warning("ibapi disconnected from tws")
        ibapp.sleep(5)
        while not ibapp.is_connected():
            try:
                logger.warning("reconnecting...")
                ibapp.connect()
            except ConnectionRefusedError as e:
                logger.warning(
                    "reconnect failed: %s, sleep for %s seconds",
                    e,
                    constants.SECONDS_BEFORE_RECONNECT,
                )
                ibapp.sleep(constants.SECONDS_BEFORE_RECONNECT)

    ibapp = AsyncIBApp(host="localhost", port=7496, client_id=1)
    ibapp.register_event_handler("connectedEvent", on_connected)
    ibapp.register_event_handler("disconnectedEvent", on_disconnected)

    ibapp.connect()
    ibapp.run()
