import pandas as pd
import json

json_example = ''' 
        [
        {"date": "2025-06-15", "open": 100, "close": 105, "volume": 3000},
        {"date": "2025-06-16", "open": 105, "close": 110, "volume": 3500}
        ]
        '''

class PandasClient:
    # Suppose you have JSON data as a string (from API or file)
    def __init__(self):
        pass
    def json_to_table(self, data):
        # if data is a string, convert to dict
        if isinstance(data, str):
            data = json.loads(data)
        # Now data is dict/list — normalize to flat table
        # Check if 'quotes' is a key containing a list of quote dicts
        if 'quotes' in data:
            df = pd.json_normalize(data['quotes'])  # normalize just the 'quotes' list into flat columns

            df['t'] = pd.to_datetime(df['t'])  # convert timestamp string to datetime object

            # Fine-grained time feature: time within the current minute
            df['time_sec'] = df['t'].dt.second + df['t'].dt.microsecond / 1e6

            # Handle cases where 'c' (conditions/exchange codes) is a list — take the first element
            df['c'] = df['c'].apply(lambda x: x[0] if isinstance(x, list) else x)

            # One-hot encode categorical columns (like exchange codes or flags)
            df = pd.get_dummies(df, columns=['ax', 'bx', 'z', 'c'])

            df = df.sort_values('t')  # sort chronologically to preserve order

            df['next_ap'] = df['ap'].shift(-1)  # next ask price

            df['label'] = (df['next_ap'] > df['ap']).astype(int)  # binary target: will ask price go up?

            #reccomendations

            # Add Mid Price: a more stable price metric
            df['mid_price'] = (df['ap'] + df['bp']) / 2

            # Add Spread: ask - bid = liquidity signal
            df['spread'] = df['ap'] - df['bp']

            # Add Order Imbalance: how much pressure on bid vs ask
            df['imbalance'] = (df['as'] - df['bs']) / (df['as'] + df['bs'] + 1e-9)  # avoid divide-by-zero

            # Add Short-Term Price Momentum
            df['price_delta'] = df['mid_price'].diff().fillna(0)

            # Add Time Between Quotes (helps detect bursts of activity)
            df['time_delta'] = df['time_sec'].diff().fillna(0)

            # Optional: Lagged Features (what was mid_price 1 or 2 steps ago)
            df['mid_price_lag1'] = df['mid_price'].shift(1)
            df['mid_price_lag2'] = df['mid_price'].shift(2)

            # Optional: Volatility (standard deviation over recent prices)
            df['rolling_vol'] = df['mid_price'].rolling(window=5).std().fillna(0)

            # Final cleanup: drop rows with any remaining NaNs from shift/rolling
            df = df.dropna()

            return df

        if 'bars' in data:
            df = pd.json_normalize(data['bars'])
            df['t'] = pd.to_datetime(df['t'])
            df = df.sort_values('t')
            #converts t col into datetime obj, sorts
            df["price_change"] = df["c"] - df["o"]
            #price change column
            df["range"] = df["h"] - df["l"]
            #price volatility during the bar
            df["volatility"] = df["range"] / df["o"]
            #normalized version of range, price movement regardless of price
            df["hour"] = df["t"].dt.hour
            df["minute"] = df["t"].dt.minute
            #time-based features
            df["future_close"] = df["c"].shift(-1)
            df["label"] = (df["future_close"] > df["c"]).astype(int)
            #predict whether price go up or down in next bar
            #shift(-1) moves c one row up comparing each row with next row
            #future_close > c becomes 1 if next bar close is higher(UP) otherwise 0 (flat or DOWN)
            df = df.dropna()
            #remove last row
            return df
        else:
            return pd.json_normalize(data)  # fallback

client = PandasClient()
# print(client.json_to_table(json_example))
