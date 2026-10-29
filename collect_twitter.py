import config
from database import Database
from twitter_collector import TwitterCollector
from datetime import datetime

def run():
    binance_database = Database()
    twitter_collector = TwitterCollector()
    try:
        if not binance_database.if_table_exist("twitter_data"):
            binance_database.create_table("twitter_data", config.TWITTER_DATA_COLUMNS, config.TWITTER_DATA_PRIMARY_KEYS)

        start_dt = datetime.strptime(config.TWITTER_START_AT, "%d %b, %Y")

        for username in config.CRYPTO_INFLUENCERS:
            latest = binance_database.get_latest_date("twitter_data", "created_at", "username", username)

            if latest:
                latest_dt = datetime.fromisoformat(latest)
                days_back = (datetime.now() - latest_dt).days + 1
                print(f"[{username}] Fetching last {days_back} days...")
            else:
                days_back = (datetime.now() - start_dt).days
                print(f"[{username}] No data found, fetching from {config.TWITTER_START_AT}...")

            df_tweets = twitter_collector.get_influencer_tweets(username, days_back=days_back)
            if not df_tweets.empty:
                binance_database.store_data(df_tweets, "twitter_data", on_conflict="IGNORE")
                print(f"✅ Stored {len(df_tweets)} tweets for {username}")
            else:
                print(f"⚠️ No new tweets for {username}")
    finally:
        binance_database.close()

if __name__ == '__main__':
    run()
