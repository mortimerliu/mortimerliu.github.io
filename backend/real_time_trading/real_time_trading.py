from typing import Dict

from kafka import KafkaConsumer
from kafka import KafkaProducer
from raw_ticker import RawTicker
from ib_insync import Ticker
from ib_insync.contract import Stock

from datetime import datetime, timedelta
import utils
import constants
from intraday_ticker import IntradayTicker, IntradayEvent

import logging

logger = logging.getLogger(__name__)

logging.getLogger("kafka").setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(constants.RTT_LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class RealTimeTrading:
    def __init__(
        self,
        contracts: list[Stock],
        bake_in_minutes: int = 0,
        bake_out_minutes: int = 0,
    ):
        self.tickers: Dict[str, IntradayTicker] = {}
        for contract in contracts:
            self.tickers[contract.symbol] = IntradayTicker(
                contract=contract,
                kafka_producer=self._producer,
            )

        self.bake_in_minutes = bake_in_minutes
        self.bake_out_minutes = bake_out_minutes

        # set up kafka consumer and producer
        self._consumer = KafkaConsumer(
            constants.RAW_TICKER_EVENT,
            bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
            key_deserializer=utils.bytes2str,
            value_deserializer=utils.bytes2object,
            auto_offset_reset="earliest",
        )
        # shared producer for all tickers
        self._producer = KafkaProducer(
            bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
            key_serializer=utils.str2bytes,
            value_serializer=utils.object2bytes,
            acks=1,
            retries=3,
            max_in_flight_requests_per_connection=1,
        )

    def is_update_window(self, dt: datetime) -> bool:
        open_, close = utils.get_market_open_close(dt)
        if open_ is None or close is None:
            return False
        open_after_bake_in = open_ + timedelta(minutes=self.bake_in_minutes)
        close_before_bake_out = close - timedelta(
            minutes=self.bake_out_minutes
        )
        return dt >= open_after_bake_in and dt < close_before_bake_out

    def _consume(self, message):
        # TODO: more efficient way to filter out old tickers
        today = utils.datetime2datestr(utils.get_today())
        raw_ticker = RawTicker.from_message(message.value)
        if utils.datetime2datestr(raw_ticker.time) < today:
            logger.warning("ticker is from previous day: %s", raw_ticker.time)
            return
        if not self.is_update_window(raw_ticker.time):
            logger.warning(
                "ticker is outside update window: %s", raw_ticker.time
            )
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
            logger.debug("consuming message: %s", msg)
            self._consume(msg)


if __name__ == "__main__":
    CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]
    rtt = RealTimeTrading(contracts=CONTRACTS)
    rtt.consume()
