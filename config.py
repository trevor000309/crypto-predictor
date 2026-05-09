#clients
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
INTERVAL = "30m"
START_AT = "1 day ago UTC"

RSI_PERIOD = 14
ATR_PERIOD = 14

PRICE_DATA_COLUMNS = [
    ('symbol', 'TEXT NOT NULL'),
    ('open_time', 'DATETIME NOT NULL'),
    ('open', 'REAL'),
    ('high', 'REAL'),
    ('low', 'REAL'),
    ('close', 'REAL'),
    ('volume', 'REAL'),
    ('number_of_trades', 'INTEGER'),
    ('taker_buy_volume', 'REAL')
]

PRICE_DATA_PRIMARY_KEYS = ['symbol', 'open_time']