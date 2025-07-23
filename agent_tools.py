from dataclasses import dataclass
from agents import (
    Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Tool, function_tool,
    set_tracing_disabled, enable_verbose_stdout_logging,Runner
)
import requests
import pandas as pd

# Optional: for debugging
enable_verbose_stdout_logging()
set_tracing_disabled(True)

# Step 1: Gemini setup using OpenAI-compatible wrapper
externalProvider = AsyncOpenAI(
    api_key="AIzaSyCSkHLFCGWSOp2nqKTAMUyXmh93sIgZBWc",  # Gemini API Key
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"  # Gemini OpenAI-compatible endpoint
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=externalProvider
)
# Step 2: Tool input/output schema
@dataclass
class CryptoPredictionInput:
    coin: str
    days: int

@dataclass
class CryptoPredictionOutput:
    coin: str
    fsym: str
    days: int
    current_price: float
    min_price: float
    max_price: float
    average_price: float
    suggested_buy_below: float
    suggested_sell_above: float

# Step 3: Define the tool
@function_tool
def predict_crypto_tool(input: CryptoPredictionInput) -> CryptoPredictionOutput:
    def get_fsym_from_name_coingecko(name: str):
        try:
            response = requests.get("https://api.coingecko.com/api/v3/search", params={"query": name})
            response.raise_for_status()
            coins = response.json().get("coins", [])
            if coins:
                return coins[0]['symbol'].upper()
        except Exception:
            return None
    print("**** in predict_crypto_tool")
    fsym = get_fsym_from_name_coingecko(input.coin)
    if not fsym:
        raise ValueError(f"❌ Coin symbol for '{input.coin}' not found.")

    try:
        response = requests.get(
            "https://min-api.cryptocompare.com/data/v2/histoday",
            params={"fsym": fsym, "tsym": "USD", "limit": input.days}
        )
        response.raise_for_status()
        data = response.json()['Data']['Data']
    except Exception as e:
        raise ValueError(f"❌ Error fetching data for {fsym}: {e}")

    df = pd.DataFrame(data)
    df['close'] = df['close'].astype(float)

    current_price = df['close'].iloc[-1]
    min_price = df['close'].min()
    max_price = df['close'].max()
    avg_price = df['close'].mean()
    suggested_buy = round(min_price * 1.03, 2)
    suggested_sell = round(max_price * 0.97, 2)
    print(f"suggested buy price {suggested_buy}")
    print(f"suggested buy price {suggested_sell}")
    return CryptoPredictionOutput(
        coin=input.coin.capitalize(),
        fsym=fsym,
        days=input.days,
        current_price=round(current_price, 2),
        min_price=round(min_price, 2),
        max_price=round(max_price, 2),
        average_price=round(avg_price, 2),
        suggested_buy_below=suggested_buy,
        suggested_sell_above=suggested_sell
    )

# Step 4: Register the tool
tools = [predict_crypto_tool]

def runAgent():
    """
    Creates and runs an AI assistant agent using Gemini (OpenAI-compatible).
    Prints the final output from the conversation.
    
    Example:
        >>> runAgent()
        The capital of a black hole is not defined...
    """
    # Create an agent with a name and some instructions
    agent = Agent(
        name="CryptoPredictor",
        model=model,
        tools=tools
    )

    # Run the agent synchronously with a given input
    response = Runner.run_sync(
        starting_agent=agent,
        input="What should I do with solana in the next 7 days?"  # Input message to the assistant
    )

    # Print the agent's final response
    print(response.final_output)

runAgent()