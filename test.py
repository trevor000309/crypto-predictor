from client import DataCollector
from config import SYMBOLS
from Database import Database
from transformers import pipeline
import requests

# Test if you can reach Binance
try:
    response = requests.get("https://api.binance.com/api/v3/ping")
    print(f"Binance API response: {response.status_code}")
    print("✅ Connection working!")
except Exception as e:
    print(f"❌ Connection failed: {e}")