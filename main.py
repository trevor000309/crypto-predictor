import config
from client import DataCollector
from config import SYMBOLS
from Database import Database
from features import FeatureEngineer
from twitter_collector import TwitterCollector
from sentiment import SentimentAnalyzer
from datetime import datetime
import pandas as pd

if __name__ == '__main__':
    binance_client = DataCollector()
    binance_database = Database()
    feature_engineer = FeatureEngineer(binance_database)
    twitter_collector = TwitterCollector()
    sentiment_analyzer = SentimentAnalyzer(binance_database)

    try:
        # --- Price Data ---
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

        # --- Feature Data ---
        for symbol in SYMBOLS:
            feature_engineer.store_features(symbol)

        # --- Twitter Data ---
        if not binance_database.if_table_exist("twitter_data"):
            binance_database.create_table("twitter_data", config.TWITTER_DATA_COLUMNS, config.TWITTER_DATA_PRIMARY_KEYS)

        start_dt = datetime.strptime(config.TWITTER_START_AT, "%d %b, %Y")

        for username in config.CRYPTO_INFLUENCERS:
            latest = binance_database.get_latest_date("twitter_data", "created_at", "username", username)
            oldest = binance_database.get_oldest_date("twitter_data", "created_at", "username", username)

            if oldest is None:
                # No data for this user — fetch full history
                days_back = (datetime.now() - start_dt).days
                print(f"[{username}] No data found, fetching from {config.TWITTER_START_AT}...")
            elif datetime.fromisoformat(oldest) > start_dt:
                # Gap at the bottom — backfill from TWITTER_START_AT (duplicates skipped by INSERT OR IGNORE)
                days_back = (datetime.now() - start_dt).days
                print(f"[{username}] Gap detected (oldest: {oldest}), backfilling from {config.TWITTER_START_AT}...")
            else:
                # Fully fetched historically — only get new tweets
                latest_dt = datetime.fromisoformat(latest)
                days_back = (datetime.now() - latest_dt).days + 1
                print(f"[{username}] Up to date, fetching last {days_back} days...")

            df_tweets = twitter_collector.get_influencer_tweets(username, days_back=days_back)
            if not df_tweets.empty:
                binance_database.store_data(df_tweets, "twitter_data", on_conflict="IGNORE")
                print(f"✅ Stored {len(df_tweets)} tweets for {username}")
            else:
                print(f"⚠️ No new tweets for {username}")

        # --- Sentiment Analysis ---
        sentiment_analyzer.analyze()

    finally:
        binance_database.close()
