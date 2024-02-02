# import nest_asyncio

# nest_asyncio.apply()

from typing import Any, ClassVar, Optional, Set
from abc import ABC, abstractmethod

import os
import signal
import json
import time
import threading
import logging
import asyncio
import websockets
from datetime import datetime
from collections import deque
from collections import defaultdict
from dataclasses import dataclass
from ibapp import AsyncIBApp
from ib_insync import IB, util, Ticker
from ib_insync.contract import Stock
import utils

from kafka import KafkaConsumer, KafkaProducer
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from handlers import RawTickerKafkaHandler, RawTickerFileHandler
from intraday_ticker import IntradayEvent
import constants

logging.getLogger("kafka").setLevel(logging.INFO)
logging.getLogger("aiokafka").setLevel(logging.INFO)
logging.getLogger("websockets").setLevel(logging.INFO)


CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(constants.APP_LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


async def join(websocket):
    print("creating kafka consumer")
    consumer = AIOKafkaConsumer(
        constants.INTRADAY_HIGH_EVENT,
        constants.INTRADAY_LOW_EVENT,
        bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
        key_deserializer=utils.bytes2str,
        value_deserializer=utils.bytes2object,
        auto_offset_reset="earliest",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            today = utils.datetime2datestr(utils.get_today())
            topic = msg.topic
            if msg.value:
                event = IntradayEvent.from_event_message(msg.value)
                if utils.datetime2datestr(event.time) < today:
                    logger.warning("skipping intraday event from previous day")
                    continue
                message = {
                    "type": topic,
                    "data": event.to_event_message(),
                }
                logger.info("sending message: %s", message)
                await websocket.send(json.dumps(message))
    finally:
        await consumer.stop()


async def handler(websocket):
    print("new connection")
    await join(websocket)


async def main():
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", 5001))
    async with websockets.serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
