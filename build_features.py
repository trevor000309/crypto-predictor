from config import SYMBOLS
from database import Database
from features import FeatureEngineer


def run():
    binance_database = Database()
    feature_engineer = FeatureEngineer(binance_database)
    try:
        for symbol in SYMBOLS:
            feature_engineer.store_features(symbol)
    finally:
        binance_database.close()


if __name__ == '__main__':
    run()
