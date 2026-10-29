import collect_binance
import build_features
import collect_twitter
import analyze_sentiment

if __name__ == '__main__':
    collect_binance.run()
    build_features.run()
    collect_twitter.run()
    analyze_sentiment.run()
