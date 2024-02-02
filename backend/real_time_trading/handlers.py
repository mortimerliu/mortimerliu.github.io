from abc import ABC, abstractmethod
from typing import Set, Optional, Any

import logging
from ib_insync import Ticker
from kafka import KafkaProducer

import utils
from raw_ticker import RawTicker


logger = logging.getLogger(__name__)


class Handler(ABC):
    @abstractmethod
    def __call__(self, tickers: Set[Ticker]):
        raise NotImplementedError


class RawTickerKafkaHandler(Handler):
    """write tickers to kafka topic"""

    def __init__(self, topic: str):
        self.topic = topic

    def _create_producer(self):
        self._producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            key_serializer=utils.str2bytes,
            value_serializer=utils.object2bytes,
            acks=1,
            retries=3,
            max_in_flight_requests_per_connection=1,
        )

    def _ticker_to_kafka_message(self, ticker: Ticker) -> dict[str, Any]:
        return RawTicker.from_ticker(ticker).to_message()

    def to_kafka(self, ticker: Ticker):
        assert ticker.contract is not None
        logger.info("sending ticker to kafka: %s", ticker.contract.symbol)
        if not hasattr(self, "_producer"):
            self._create_producer()
        assert ticker.contract is not None
        self._producer.send(
            self.topic,
            key=ticker.contract.symbol,
            value=self._ticker_to_kafka_message(ticker),
        )

    def __call__(self, tickers: Set[Ticker]):
        for ticker in tickers:
            self.to_kafka(ticker)


class RawTickerFileHandler(Handler):
    """write tickers to file"""

    def __init__(
        self,
        directory: str,
        filename_prefix: Optional[str] = None,
        mode: str = "a",
    ):
        self.directory = directory
        utils.makedirs(self.directory)
        self.filename_prefix = filename_prefix

    def _get_filename(self, symbol: str) -> str:
        prefix = self.filename_prefix
        if not prefix:
            today = utils.datetime2datestr(
                utils.get_local_now(), format="%Y%m%d"
            )
            prefix = f"raw_ticker_{today}"
        return f"{self.directory}/{prefix}_{symbol}.txt"

    def __call__(self, tickers: Set[Ticker]):
        for ticker in tickers:
            assert ticker.contract is not None
            filename = self._get_filename(ticker.contract.symbol)
            with open(filename, "a") as f:
                f.write(f"{ticker}\n")
