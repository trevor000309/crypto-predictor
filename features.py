import pandas as pd
import numpy as np
import config
from database import Database

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

        ma7 = df["close"].rolling(window=7).mean()
        ma25 = df["close"].rolling(window=25).mean()

        df["dist_ma25"] = (df["close"] - ma25) / ma25
        df["ma_spread"] = (ma7 - ma25) / ma25

        # percentage change from previous close
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))

        raw_ATR = self.calculate_atr(df)
        df["RSI"] = self.calculate_rsi(df["close"])
        df["ATR_percentage"] = raw_ATR / df["close"]

        is_up = df["close"] > df["open"]
        is_down = df["close"] < df["open"]

        up_id = (is_up != is_up.shift(1)).cumsum()
        df["consecutive_up"] = is_up.groupby(up_id).cumsum()

        down_id = (is_down != is_down.shift(1)).cumsum()
        df["consecutive_down"] = is_down.groupby(down_id).cumsum()

        # 1 = next candle up, -1 = next candle down
        upper_bound = df["close"] + 1.75 * raw_ATR
        lower_bound = df["close"] - 1.75 * raw_ATR
        label = pd.Series(0, index=df.index)
        resolved = pd.Series(False, index=df.index)

        for i in range(1, config.FUTURE_WINDOW + 1):
            hit_upper = (df["high"].shift(-i) > upper_bound) & (~resolved)
            hit_lower = (df["low"].shift(-i) < lower_bound) & (~resolved)

            label[hit_upper & ~hit_lower] = 1
            label[hit_lower & ~hit_upper] = -1
            label[hit_upper & hit_lower] = -1 # If both are hit, prioritize down movement

            resolved[hit_upper | hit_lower] = True

        df["label"] = label

        # Drop NaN rows from rolling calculations and the last row (label unknown)
        df = df.dropna().iloc[:-config.FUTURE_WINDOW]

        return df[["symbol", "open_time", "dist_ma25", "ma_spread", "RSI", "ATR_percentage", "log_return", "consecutive_up", "consecutive_down", "label"]]

    def store_features(self, symbol):
        if not self.db.if_table_exist("feature_data"):
            self.db.create_table("feature_data", config.FEATURE_DATA_COLUMNS, config.FEATURE_DATA_PRIMARY_KEYS)

        df = self.compute_features(symbol)
        self.db.store_data(df, "feature_data", on_conflict="REPLACE")
        print(f"Stored features for {symbol}: {len(df)} rows")
