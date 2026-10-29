import pandas as pd
from transformers import pipeline
from database import Database

class SentimentAnalyzer:
    def __init__(self, database: Database):
        self.db = database
        print("Loading sentiment model...")
        self.model = pipeline(
            "text-classification",
            model="ElKulako/cryptobert",
            truncation=True,
            max_length=512
        )
        print("Model loaded.")

    def _to_score(self, label, score):
        # ElKulako/cryptobert labels: Bullish, Neutral, Bearish
        if label == "Bullish":
            return round(score, 4)
        elif label == "Bearish":
            return round(-score, 4)
        else:
            return 0.0

    def analyze(self, batch_size: int = 32):
        df = pd.read_sql(
            "SELECT id, text FROM twitter_data WHERE sentiment IS NULL",
            self.db.conn
        )

        if df.empty:
            print("No tweets to analyze.")
            return

        print(f"Analyzing sentiment for {len(df)} tweets...")

        texts = df["text"].tolist()
        scores = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            results = self.model(batch)
            for result in results:
                scores.append(self._to_score(result["label"], result["score"]))

            print(f"{min(i + batch_size, len(texts))}/{len(df)} tweets processed...")

        df["sentiment"] = scores

        self.db.conn.executemany(
            "UPDATE twitter_data SET sentiment = ? WHERE id = ?",
            list(zip(df["sentiment"], df["id"]))
        )
        self.db.conn.commit()
        print(f"✅ Sentiment updated for {len(df)} tweets")