import config
from binance_collector import DataCollector
from config import SYMBOLS
from database import Database

def run():
    binance_client = DataCollector()
    binance_database = Database()
    try:
        if not binance_database.if_table_exist("price_data"):
            binance_database.create_table("price_data", config.PRICE_DATA_COLUMNS, config.PRICE_DATA_PRIMARY_KEYS)

        for symbol in SYMBOLS:
            latest = binance_database.get_latest_date("price_data", "open_time", "symbol", symbol)

            if latest:
                print(f"[{symbol}] Fetching new data since {latest}...")
            else:
                print(f"[{symbol}] No data found, fetching from {config.START_AT}...")

            df = binance_client.get_formated_data(symbol, start_str=latest)
            print(df)
            binance_database.store_data(df, "price_data")
    finally:
        binance_database.close()

if __name__ == '__main__':
    run()
