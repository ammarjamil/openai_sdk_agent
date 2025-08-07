import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv('GOOGLE_API_KEY'))

def predict_any_crypto(coin, days):
    """
    Predicts buying/selling/holding thresholds for any crypto coin based on historical price data.
    
    Parameters:
        coin (str): Coin name (e.g., 'bitcoin', 'solana', 'dogecoin')
        days (int): Number of historical days to analyze

    Output:
        Prints key price stats and suggested buy/sell levels.
    """

    def get_fsym_from_name_coingecko(name):
        """Fetch the ticker symbol (fsym) from CoinGecko using coin name"""
        try:
            response = requests.get("https://api.coingecko.com/api/v3/search", params={"query": name})
            response.raise_for_status()
            coins = response.json().get("coins", [])
            if coins:
                return coins[0]['symbol'].upper()
        except Exception as e:
            print(f"❌ Error getting symbol for '{name}': {e}")
        return None

    fsym = get_fsym_from_name_coingecko(coin)
    if not fsym:
        print(f"❌ Coin symbol for '{coin}' not found.")
        return

    try:
        response = requests.get(
            "https://min-api.cryptocompare.com/data/v2/histoday",
            params={'fsym': fsym, 'tsym': 'USD', 'limit': days}
        )
        response.raise_for_status()
        data = response.json()['Data']['Data']
    except Exception as e:
        print(f"❌ Error fetching historical data for {fsym}: {e}")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['close'] = df['close'].astype(float)

    # Key metrics
    current_price = df['close'].iloc[-1]
    min_price = df['close'].min()
    max_price = df['close'].max()
    avg_price = df['close'].mean()
    suggested_buy = round(min_price * 1.03, 2)
    suggested_sell = round(max_price * 0.97, 2)

    coin_name_formatted = coin.capitalize()

    # Display result
    print(f"📊 {coin_name_formatted} ({fsym}) – {days}-Day Price Analysis")
    print(f"- Current Price:   ${current_price:.2f}")
    print(f"- Lowest Price:    ${min_price:.2f}")
    print(f"- Highest Price:   ${max_price:.2f}")
    print(f"- Average Price:   ${avg_price:.2f}")
    print()
    print(f"📉 Suggested Buy Below:  ${suggested_buy}")
    print(f"📈 Suggested Sell Above: ${suggested_sell}")




