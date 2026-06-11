import pandas as pd
import config
from Database import Database


class FeatureEngineer:
    def __init__(self, database: Database):
        self.db = database

    def load_price_data(self, symbol):
        df = pd.read_sql(
            "SELECT * FROM price_data WHERE symbol = ? ORDER BY open_time ASC",
            self.db.conn,
            params=(symbol,)
        )
        df["open_time"] = pd.to_datetime(df["open_time"])
        for col in ["open", "high", "low", "close", "volume", "taker_buy_volume"]:
            df[col] = df[col].astype(float)
        return df

    def calculate_rsi(self, series):
        #https://www.investopedia.com/terms/r/rsi.asp
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / config.RSI_PERIOD, min_periods=config.RSI_PERIOD, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / config.RSI_PERIOD, min_periods=config.RSI_PERIOD, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_atr(self, df):
        #https://www.investopedia.com/terms/a/atr.asp
        prev_close = df["close"].shift(1)
        tr = pd.concat([
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs()
        ], axis=1).max(axis=1)
        return tr.ewm(alpha=1 / config.ATR_PERIOD, adjust=False).mean()

    def compute_features(self, symbol):
        df = self.load_price_data(symbol)

        df["rsi"] = self.calculate_rsi(df["close"])
        df["atr"] = self.calculate_atr(df)
        df["ma7"] = df["close"].rolling(window=7).mean()
        df["ma25"] = df["close"].rolling(window=25).mean()
        df["price_change_pct"] = df["close"].pct_change() * 100
        # 1 = next candle up, 0 = next candle down
        df["label"] = (df["close"].shift(-1) > df["close"]).astype(int)

        # Drop NaN rows from rolling calculations and the last row (label unknown)
        df = df.dropna().iloc[:-1]

        return df[["symbol", "open_time", "rsi", "atr", "ma7", "ma25", "price_change_pct", "label"]]

    def store_features(self, symbol):
        if not self.db.if_table_exist("feature_data"):
            self.db.create_table("feature_data", config.FEATURE_DATA_COLUMNS, config.FEATURE_DATA_PRIMARY_KEYS)

        df = self.compute_features(symbol)
        self.db.store_data(df, "feature_data", on_conflict="REPLACE")
        print(f"Stored features for {symbol}: {len(df)} rows")
