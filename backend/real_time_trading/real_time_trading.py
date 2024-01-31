from typing import Dict

from kafka import KafkaConsumer
from kafka import KafkaProducer
from raw_ticker import RawTicker
from ib_insync import Ticker
from ib_insync.contract import Stock

import utils
import constants
from intraday_ticker import IntradayTicker, IntradayEvent

import logging

logger = logging.getLogger(__name__)

logging.getLogger("kafka").setLevel(logging.DEBUG)


class RealTimeTrading:
    def __init__(self, contracts: list[Stock]):
        self.today = utils.datetime2datestr(utils.get_today())
        self.topic = constants.RAW_TICKER_EVENT
        self._consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
            key_deserializer=utils.bytes2str,
            value_deserializer=utils.bytes2object,
            auto_offset_reset="earliest",
        )
        self._producer = KafkaProducer(
            bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
            key_serializer=utils.str2bytes,
            value_serializer=utils.object2bytes,
            acks=1,
            retries=3,
            max_in_flight_requests_per_connection=1,
        )
        self.tickers: Dict[str, IntradayTicker] = {}
        for contract in contracts:
            self.tickers[contract.symbol] = IntradayTicker(
                contract=contract,
                kafka_producer=self._producer,
            )

    def _consume(self, message):
        raw_ticker = RawTicker.from_message(message.value)
        if utils.datetime2datestr(raw_ticker.time) < self.today:
            logger.warning("ticker is from previous day: %s", raw_ticker.time)
            return
        intraday_ticker = self.tickers.get(raw_ticker.symbol)
        if intraday_ticker is None:
            logger.warning(
                "ticker not found for symbol: %s", raw_ticker.symbol
            )
            return
        intraday_ticker.update(raw_ticker)

    def consume(self):
        for msg in self._consumer:
            print(msg)
            self._consume(msg)


if __name__ == "__main__":
    CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]
    rtt = RealTimeTrading(contracts=CONTRACTS)
    rtt.consume()
