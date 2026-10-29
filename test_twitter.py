from twitter_collector import TwitterCollector

collector = TwitterCollector()

# Test with just 1 influencer, 1 day — no database touched
df = collector.get_influencer_tweets("saylor", days_back=30)

print(df)
print(f"\nTotal tweets: {len(df)}")
