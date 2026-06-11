from binance.client import Client
import pandas as pd
import config

class DataCollector:
    def __init__(self):
        self.client = Client()

    def get_data(self, symbol):
        klines = self.client.get_historical_klines(symbol, config.INTERVAL, config.START_AT)
        #(Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, Taker buy quote asset volume, Ignore)
        return klines

    def get_formated_data(self, symbol):
        klines = self.get_data(symbol)

        essential_data = [[kline[i] for i in [0,1,2,3,4,5,8,9]] for kline in klines]
        df = pd.DataFrame(essential_data, columns=["open_time", "open", "high", "low", "close", "volume", "number_of_trades", "taker_buy_volume"])

        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.insert(0, "symbol", symbol)

        numeric_cols = ["open", "high", "low", "close", "volume", "number_of_trades", "taker_buy_volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)

        return df