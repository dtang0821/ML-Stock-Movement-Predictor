import requests
from alpaca_py.config import API_KEY, SECRET_KEY, MARKET_DATA_URL

BASE_URL = "https://paper-api.alpaca.markets"
class AlpacaClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "application/json",
            "APCA-API-KEY-ID": API_KEY,
            "APCA-API-SECRET-KEY": SECRET_KEY
        })

    def get_account(self):
        url = f"{BASE_URL}/v2/account"
        response = self.session.get(url)
        return response.json()

    
    #url = "https://data.alpaca.markets/v2/stocks/bars?symbols=AAPL&timeframe=1Hour&limit=3&adjustment=raw&feed=sip&sort=asc"
    #can use params object to fill the end of the parameters without editing url again
    def get_bars(self, symbol: str, timeframe: str = "1Day", limit: int = 5, sort: str = "asc"):
        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
        params = {
            "timeframe": timeframe,
            "limit": limit,
            "sort": sort
        }
        response = self.session.get(url, params=params)
        return response.json()
    
    #url = "https://data.alpaca.markets/v2/stocks/AAPL/quotes/latest?feed=iex&currency=USD"
    def get_quote(self, symbol: str, feed: str = "iex", currency: str = "USD"):
        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes"
        params = {
            "feed": feed,
            "currency": currency
        }
        response = self.session.get(url, params=params)
        return response.json()
    
        

