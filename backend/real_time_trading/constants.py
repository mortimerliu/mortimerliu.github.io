# list of contracts to be monitored
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

RAW_TICKER_EVENT = "raw_ticker"
INTRADAY_HIGH_EVENT = "intraday_high"
INTRADAY_LOW_EVENT = "intraday_low"
BUY_ORDER_EVENT = "buy_order"
SELL_ORDER_EVENT = "sell_order"

KAFKA_HOST = "localhost"
KAFKA_PORT = 9092
KAFKA_BOOTSTRAP_SERVERS = f"{KAFKA_HOST}:{KAFKA_PORT}"


IBAPP_LOG_FILE = "logs/ibapp.log"
RTT_LOG_FILE = "logs/real_time_trading.log"
APP_LOG_FILE = "logs/app.log"
