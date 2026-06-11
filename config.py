#clients
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
INTERVAL = "30m"
START_AT = "1 Jan, 2024 UTC"
TWITTER_START_AT = "1 Jan, 2024"

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

FEATURE_DATA_COLUMNS = [
    ('symbol', 'TEXT NOT NULL'),
    ('open_time', 'DATETIME NOT NULL'),
    ('rsi', 'REAL'),
    ('atr', 'REAL'),
    ('ma7', 'REAL'),
    ('ma25', 'REAL'),
    ('price_change_pct', 'REAL'),
    ('label', 'INTEGER')
]

FEATURE_DATA_PRIMARY_KEYS = ['symbol', 'open_time']

CRYPTO_INFLUENCERS = [
    "saylor",
    "cz_binance",
    "VitalikButerin",
    "realDonaldTrump"
]

TWITTER_DATA_COLUMNS = [
    ('id', 'TEXT NOT NULL'),
    ('username', 'TEXT NOT NULL'),
    ('text', 'TEXT'),
    ('created_at', 'DATETIME NOT NULL'),
    ('like_count', 'INTEGER'),
    ('retweet_count', 'INTEGER'),
    ('view_count', 'INTEGER'),
    ('is_retweet', 'INTEGER'),
    ('lang', 'TEXT'),
    ('is_influencer', 'INTEGER'),
    ('sentiment', 'REAL')
]

TWITTER_DATA_PRIMARY_KEYS = ['id']