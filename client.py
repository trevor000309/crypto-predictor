from binance.client import Client
import pandas as pd
import config
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime
import os

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
        df = pd.DataFrame(essential_data, columns=["Open time", "Open price", "Highest", "Lowest", "Close price", "Volume", "Number of trades", "Taker buy volume"])

        df["Open time"] = pd.to_datetime(df["Open time"], unit = "ms")

        return df