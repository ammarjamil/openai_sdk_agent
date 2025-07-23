from dotenv import load_dotenv
load_dotenv()
import requests
import os
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
import pandas as pd

# Set your API keys
# Define tools
@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    print("in add from tool")
    return a - b

@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    print("in subtract from tool")

    return a * b

@tool
def predict_crypto_rate(coin: str = "bitcoin") -> str:
    """
    Predict crypto buying/selling rate based on current price trend.
    Supported coins: bitcoin, ethereum, etc.
    """
    print("in predict_crypto_rate")
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"Error fetching price for {coin}"
    
    price = response.json().get(coin, {}).get("usd")
    
    if not price:
        return f"Could not get USD price for {coin}"

    # Dummy logic: if price is high, suggest selling, if low, suggest buying
    suggestion = "buy" if price < 20000 else "sell" if price > 40000 else "hold"
    
    return f"{coin.capitalize()} price is ${price}. Suggested action: {suggestion}"

@tool
def analyze_all_coins() -> str:
    """
    Analyze top 10 crypto coins and suggest Buy/Hold/Sell based on price.
    Uses dummy rules: Buy if < $1000, Sell if > $30,000, else Hold.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return "Error fetching coin data."

    coins = response.json()
    result = []

    for coin in coins:
        name = coin["name"]
        price = coin["current_price"]

        # Dummy prediction logic
        if price < 1000:
            action = "Buy"
        elif price > 30000:
            action = "Sell"
        else:
            action = "Hold"

        result.append(f"{name}: ${price} → {action}")

    return "\n".join(result)


@tool
def predict_any_crypto(coin :str, days:int)-> str:
    """
    Predicts buying/selling/holding thresholds for any crypto coin based on historical price data.
    
    Parameters:
        coin (str): Coin name (e.g., 'bitcoin', 'solana', 'dogecoin')
        days (int): Number of historical days to analyze

    Output:
        Prints key price stats and suggested buy/sell levels.
    """
    print("in predict_any_crypto")
    def get_fsym_from_name_coingecko(name):
        """Fetch the ticker symbol (fsym) from CoinGecko using coin name"""
        try:
            response = requests.get("https://api.coingecko.com/api/v3/search", params={"query": name})
            response.raise_for_status()
            coins = response.json().get("coins", [])
            if coins:
                return coins[0]['symbol'].upper()
        except Exception as e:
            return f"❌ Error getting symbol for '{name}': {e}"

    fsym = get_fsym_from_name_coingecko(coin)
    if not fsym:
        return f"❌ Coin symbol for '{coin}' not found."

    try:
        response = requests.get(
            "https://min-api.cryptocompare.com/data/v2/histoday",
            params={'fsym': fsym, 'tsym': 'USD', 'limit': days}
        )
        response.raise_for_status()
        data = response.json()['Data']['Data']
    except Exception as e:
        
        return f"❌ Error fetching historical data for {fsym}: {e}"

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
    return {
        "coin": coin.capitalize(),
        "fsym": fsym,
        "days": days,
        "current_price": round(current_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "average_price": round(avg_price, 2),
        "suggested_buy_below": suggested_buy,
        "suggested_sell_above": suggested_sell
    }

tools = [add, subtract,predict_crypto_rate,analyze_all_coins,predict_any_crypto]

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run a test
response = agent.invoke("Predict what I should do with xrp with 7 days")

# print(response)