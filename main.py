from dotenv import load_dotenv
load_dotenv()
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

tools = [add, subtract]

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
response = agent.invoke("What is 15 plus 5?")

print(response)