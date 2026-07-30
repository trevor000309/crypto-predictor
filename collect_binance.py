import config
from binance_collector import DataCollector
from config import SYMBOLS
from database import Database


def run():
    binance_client = DataCollector()
    binance_database = Database()
    try:
        if binance_database.if_table_exist("price_data"):
            for symbol in SYMBOLS:
                df = binance_client.get_formated_data(symbol)
                print(df)
                binance_database.store_data(df, "price_data")
        else:
            binance_database.create_table("price_data", config.PRICE_DATA_COLUMNS, config.PRICE_DATA_PRIMARY_KEYS)
            for symbol in SYMBOLS:
                df = binance_client.get_formated_data(symbol)
                print(df)
                binance_database.store_data(df, "price_data")
    finally:
        binance_database.close()


if __name__ == '__main__':
    run()
