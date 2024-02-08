# list of contracts to be monitored
from __future__ import annotations

import json

CONTRACT_TYPE = dict[str, str]

ROOT_DIR: str = "/home/hongruliu/src/real-time-trading"
IBAPP_LOG_FILE: str = f"{ROOT_DIR}/logs/ibapp.log"
RTT_LOG_FILE: str = f"{ROOT_DIR}/logs/real_time_trading.log"
APP_LOG_FILE: str = f"{ROOT_DIR}/logs/app.log"
DATA_DIR: str = f"{ROOT_DIR}/data/raw_ticker"
CONTRACTS_FILE: str = f"{ROOT_DIR}/contracts.json"

RAW_TICKER_EVENT: str = "raw_ticker"
INTRADAY_HIGH_EVENT: str = "intraday_high"
INTRADAY_LOW_EVENT: str = "intraday_low"
TOP_HIGH_EVENT: str = "top_high"
TOP_LOW_EVENT: str = "top_low"
BUY_ORDER_EVENT: str = "buy_order"
SELL_ORDER_EVENT: str = "sell_order"

KAFKA_HOST: str = "localhost"
KAFKA_PORT: int = 9092
KAFKA_BOOTSTRAP_SERVERS: str = f"{KAFKA_HOST}:{KAFKA_PORT}"

SECONDS_BEFORE_RECONNECT: int = 20

CONTRACTS: list[CONTRACT_TYPE] = []
try:
    with open(CONTRACTS_FILE) as f:
        CONTRACTS = json.load(f)
except FileNotFoundError:
    CONTRACTS = [
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
