from database import Database
from sentiment import SentimentAnalyzer

def run():
    db = Database()
    try:
        analyzer = SentimentAnalyzer(db)
        analyzer.analyze()
    finally:
        db.close()

if __name__ == '__main__':
    run()
