from dotenv import load_dotenv
load_dotenv()
import requests
import os
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType


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
def predict_any_crypto(coin: str) -> str:
    """
    Predicts buying/selling/holding decision for any crypto coin based on current price.
    Example coin names: bitcoin, ethereum, dogecoin, solana, etc.
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"Error fetching price for '{coin}'"

    price_data = response.json().get(coin)
    if not price_data:
        return f"Coin '{coin}' not found on CoinGecko."

    price = price_data.get("usd")

    # Dummy logic: Replace with real model later
    if price < 1:
        suggestion = "Buy"
    elif price > 30000:
        suggestion = "Sell"
    else:
        suggestion = "Hold"

    return f"{coin.capitalize()} current price is ${price}. Suggested action: {suggestion}"

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
response = agent.invoke("Predict what I should do with solana and dogecoin.")

print(response)