"""
LangChain crypto trading agent using HKBU GenAI API (Azure OpenAI format).
"""
import os

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from agent.tools import create_tools


def create_crypto_agent(user_id: str = "user_default"):
    """Create crypto trading agent with tools bound to user_id."""
    api_key = os.getenv("HKBU_API_KEY")
    base_url = os.getenv("HKBU_BASE_URL", "https://genai.hkbu.edu.hk/api/v0/rest")
    model = os.getenv("HKBU_MODEL", "gemini-2.5-flash")
    api_version = os.getenv("HKBU_API_VERSION", "v1")

    if not api_key:
        raise ValueError("HKBU_API_KEY environment variable is required")

    llm = AzureChatOpenAI(
        azure_endpoint=base_url,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=model,
        temperature=0,
        streaming=False,
    )

    tools = create_tools(user_id)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful cryptocurrency trading assistant. Your tasks:
1. Get real-time crypto prices from Binance
2. Show order book depth
3. Execute simulated buys (real prices, simulated wallet - no real money)
4. Show wallet balance and transaction history

Rules:
- Always confirm price and amount before executing a buy
- Respond in English
- If the user has insufficient balance, explain clearly
- Supported pairs: BTC, ETH, SOL, BNB, etc. (use /USDT format when needed)""",
            ),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )
    executor.agent.stream_runnable = False

    return executor
