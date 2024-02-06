# list of contracts to be monitored
from __future__ import annotations

CONTRACT_TYPE = dict[str, str]

CONTRACTS: list[CONTRACT_TYPE] = [
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

ROOT_DIR: str = "~/src/real-time-trading"

IBAPP_LOG_FILE: str = f"{ROOT_DIR}/logs/ibapp.log"
RTT_LOG_FILE: str = f"{ROOT_DIR}/logs/real_time_trading.log"
APP_LOG_FILE: str = f"{ROOT_DIR}/logs/app.log"

SECONDS_BEFORE_RECONNECT: int = 20
