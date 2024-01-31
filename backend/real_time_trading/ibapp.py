from abc import ABC, abstractmethod
import pickle
import logging
from typing import List, Set, Callable

from ib_insync import IB, util, Ticker
from ib_insync.contract import Stock

import constants
from handlers import Handler, RawTickerKafkaHandler, RawTickerFileHandler

logging.getLogger("kafka").setLevel(logging.INFO)

util.logToConsole(logging.INFO)


class AsyncIBApp:
    """Wrapper class for ib_insync.IB."""

    def __init__(self, host: str, port: int, client_id: int):
        self.host = host
        self.port = port
        self.client_id = client_id
        self._ib = IB()

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

    def run(self):
        self._ib.run()


if __name__ == "__main__":
    CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]

    ibapp = AsyncIBApp(host="localhost", port=7496, client_id=1)
    ibapp.connect()

    raw_ticker_kafka_handler = RawTickerKafkaHandler(
        topic=constants.RAW_TICKER_EVENT
    )
    raw_ticker_file_handler = RawTickerFileHandler(directory="data/raw_ticker")
    ibapp.request_market_data(
        contracts=CONTRACTS,
        callbacks=[raw_ticker_kafka_handler, raw_ticker_file_handler],
    )
    ibapp.run()
