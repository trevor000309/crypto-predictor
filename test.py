from datetime import datetime, timezone, timedelta
from client import DataCollector
from config import SYMBOLS
from Database import Database
from transformers import pipeline
import requests

# Test if you can reach Binance
"""
try:
    response = requests.get("https://api.binance.com/api/v3/ping")
    print(f"Binance API response: {response.status_code}")
    print("✅ Connection working!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
"""

"""
print(datetime.now(timezone.utc) - timedelta(days=730))
print(datetime.strptime("Sun Jun 07 21:16:18 +0000 2026", "%a %b %d %H:%M:%S +0000 %Y"))
print(datetime.strptime("Sun Jun 07 21:16:18 +0000 2026", "%a %b %d %H:%M:%S +0000 %Y").replace(tzinfo=timezone.utc))
'''