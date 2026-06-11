import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import time
import config

load_dotenv()

class TwitterCollector:
    def __init__(self):
        self.api_key = os.environ.get("TWITTER_API_KEY")

    def _extract_text(self, tweet: dict):
        # Use original text if it's a retweet
        if tweet.get("retweeted_tweet"):
            return tweet["retweeted_tweet"]["text"]
        return tweet["text"]

    def get_influencer_tweets(self, username: str, days_back: int = 730):
        # https://docs.twitterapi.io/api-reference/endpoint/get_user_last_tweets
        url = f"https://api.twitterapi.io/twitter/user/last_tweets"
        headers = {"X-API-Key": self.api_key}
        params = {"userName": username}

        cursor = ""
        all_tweets = []

        print(f"Fetching tweets for {username}...")

        cutoff_date = datetime.now() - timedelta(days = days_back)
        while True:
            params["cursor"] = cursor

            for attempt in range(3):
                try:
                    response = requests.get(url, headers=headers, params=params)
                    data = response.json()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < 2:
                        print(f"Request failed ({e}), retrying in 5s...")
                        time.sleep(5)
                    else:
                        print(f"Failed after 3 attempts for {username}")
                        return pd.DataFrame(all_tweets)

            if data.get("status") != "success":
                print(f"Error when fetching tweets for {username}: {data.get('msg')}")
                break

            tweets = data["data"]["tweets"]

            for tweet in tweets:
                created_at = datetime.strptime((tweet["createdAt"]), "%a %b %d %H:%M:%S +0000 %Y")

                # Stop paginating if tweets are older than cutoff
                if created_at < cutoff_date:
                    print(f"Fetching done for {username} — stopping")
                    return pd.DataFrame(all_tweets)

                all_tweets.append({
                    "id":            tweet["id"],
                    "username":      username,
                    "text":          self._extract_text(tweet),
                    "created_at":    created_at,
                    "like_count":    tweet.get("likeCount", 0),
                    "retweet_count": tweet.get("retweetCount", 0),
                    "view_count":    tweet.get("viewCount", 0),
                    "is_retweet":    int(tweet.get("retweeted_tweet") is not None),
                    "lang":          tweet.get("lang", ""),
                    "is_influencer": 1,
                    "sentiment":     None
                })

            cursor = data.get("next_cursor")
            if not cursor:
                print(f"Finished fetching for {username}")
                break

            print(f"{len(all_tweets)} tweets collected so far...")

        return pd.DataFrame(all_tweets)

    def get_all_influencer_tweets(self, days_back: int = 730):
        all_dfs = []

        for username in config.CRYPTO_INFLUENCERS:
            df = self.get_influencer_tweets(username, days_back)
            if not df.empty:
                all_dfs.append(df)
                print(f"✅ {username}: {len(df)} tweets collected")
            else:
                print(f"⚠️ {username}: no tweets found")

        if not all_dfs:
            return pd.DataFrame()

        return pd.concat(all_dfs, ignore_index=True)
