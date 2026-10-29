#clients
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
INTERVAL = "30m"
START_AT = "1 Jan, 2024 UTC"
TWITTER_START_AT = "1 Jan, 2024"

RSI_PERIOD = 14
ATR_PERIOD = 14

FUTURE_WINDOW = 5

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
    ('dist_ma25', 'REAL'),
    ('ma_spread', 'REAL'),
    ('RSI', 'REAL'),
    ('ATR_percentage', 'REAL'),
    ('log_return', 'REAL'),
    ('consecutive_up', 'INTEGER'),
    ('consecutive_down', 'INTEGER'),
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

TRAIN_FEATURES['']