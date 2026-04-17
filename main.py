from client import DataCollector
from config import SYMBOLS
import pandas as pd

if __name__ == '__main__':
    binance_client = DataCollector()
    for symbol in SYMBOLS:
        print(binance_client.get_formated_data(symbol))