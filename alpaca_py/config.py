import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("api_key")
SECRET_KEY = os.getenv("secret_key") 
BASE_URL = "https://paper-api.alpaca.markets"
MARKET_DATA_URL = "https://data.alpaca.markets"