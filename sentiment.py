import pandas as pd
from transformers import pipeline
from Database import Database

class SentimentAnalyzer:
    def __init__(self, database: Database):
        self.db = database
        print("Loading sentiment model...")
        self.model = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment",
            truncation=True,
            max_length=512
        )
        print("Model loaded.")

    def _to_score(self, label: str, score: float) -> float:
        # LABEL_0 = Negative, LABEL_1 = Neutral, LABEL_2 = Positive
        if label == "LABEL_2":
            return round(score, 4)
        elif label == "LABEL_0":
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

            print(f"  {min(i + batch_size, len(texts))}/{len(df)} tweets processed...")

        df["sentiment"] = scores

        self.db.conn.executemany(
            "UPDATE twitter_data SET sentiment = ? WHERE id = ?",
            list(zip(df["sentiment"], df["id"]))
        )
        self.db.conn.commit()
        print(f"✅ Sentiment updated for {len(df)} tweets")
