# import nest_asyncio
# nest_asyncio.apply()
from __future__ import annotations

import asyncio
import json
import logging
import os
import signal

import websockets
from aiokafka import AIOKafkaConsumer
from ib_insync.contract import Stock
from real_time_trading import constants
from real_time_trading import utils
from real_time_trading.objects.intraday_ticker import IntradayEvent
from real_time_trading.objects.top_symbol import TopNSymbols


logging.getLogger("kafka").setLevel(logging.INFO)
logging.getLogger("aiokafka").setLevel(logging.INFO)
logging.getLogger("websockets").setLevel(logging.INFO)


CONTRACTS = [Stock(**stk) for stk in constants.CONTRACTS]

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(constants.APP_LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


async def send_intraday_event(websocket, topic, message):
    today = utils.datetime2datestr(utils.get_local_now())
    event = IntradayEvent.from_event_message(message)
    if utils.datetime2datestr(event.time.to_timezone()) < today:
        logger.warning("skipping intraday event from previous day")
        return
    message = {
        "type": topic,
        "data": event.to_event_message(local_time=True),
    }
    logger.info("sending message: %s", message)
    await websocket.send(json.dumps(message))


async def send_top_event(websocket, topic, message):
    today = utils.datetime2datestr(utils.get_local_now())
    logger.debug("today: %s", today)
    event = TopNSymbols.from_message(message)
    logger.debug("event: %s", event)
    if utils.datetime2datestr(event.time.to_timezone()) < today:
        logger.warning("skipping top event from previous day")
        return
    message = {
        "type": topic,
        "data": event.to_message_only_data(),
    }
    logger.info("sending message: %s", message)
    await websocket.send(json.dumps(message))


async def consume_intraday_events(websocket):
    logger.info("creating kafka consumer for intraday events")
    consumer = AIOKafkaConsumer(
        constants.INTRADAY_HIGH_EVENT,
        constants.INTRADAY_LOW_EVENT,
        bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
        key_deserializer=utils.bytes2str,
        value_deserializer=utils.bytes2object,
        auto_offset_reset="earliest",
    )
    await consumer.start()  # type: ignore
    await utils.set_offsets_by_time_aiokafka(consumer)
    try:
        async for msg in consumer:
            if msg.value:
                await send_intraday_event(websocket, msg.topic, msg.value)
    finally:
        await consumer.stop()  # type: ignore


async def consume_top_symbol_events(websocket):
    logger.info("creating kafka consumer for top symbol events")
    consumer = AIOKafkaConsumer(
        constants.TOP_HIGH_EVENT,
        constants.TOP_LOW_EVENT,
        bootstrap_servers=constants.KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=utils.bytes2object,
        auto_offset_reset="earliest",
    )
    await consumer.start()  # type: ignore
    await utils.set_offsets_by_time_aiokafka(consumer)
    try:
        async for msg in consumer:
            if msg.value:
                await send_top_event(websocket, msg.topic, msg.value)
    finally:
        await consumer.stop()  # type: ignore


async def handler(websocket):
    logger.info("new connection")
    intraday_task = asyncio.create_task(consume_intraday_events(websocket))
    top_symbol_task = asyncio.create_task(consume_top_symbol_events(websocket))
    await asyncio.gather(intraday_task, top_symbol_task)


async def main():
    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT", 5001))
    async with websockets.serve(handler, "", port):
        await stop


if __name__ == "__main__":
    asyncio.run(main())
