import config
from client import DataCollector
from config import SYMBOLS
from Database import Database
from features import FeatureEngineer
import pandas as pd

if __name__ == '__main__':
    binance_client = DataCollector()
    binance_database = Database()
    feature_engineer = FeatureEngineer(binance_database)

    if binance_database.if_table_exist("price_data"):
        for symbol in SYMBOLS:
            df = binance_client.get_formated_data(symbol)
            print(df)
            binance_database.store_data(df, "price_data")
    else:
        for symbol in SYMBOLS:
            df = binance_client.get_formated_data(symbol)
            print(df)
            binance_database.create_table("price_data", config.PRICE_DATA_COLUMNS, config.PRICE_DATA_PRIMARY_KEYS)
            binance_database.store_data(df, "price_data")

    for symbol in SYMBOLS:
        feature_engineer.store_features(symbol)
