"""
Factory that creates a fully-registered MCPSimulator for a given user.
"""
from functools import partial

from mcp_server.simulator import MCPSimulator
from mcp_server.handlers import (
    handle_get_price,
    handle_get_orderbook,
    handle_buy_crypto,
    handle_check_balance,
    handle_transaction_history,
)
from db.mongo import insert_mcp_log


def create_mcp_server(user_id: str) -> MCPSimulator:
    """Instantiate an MCP simulator and register all crypto tools."""
    persist = partial(insert_mcp_log, user_id)
    mcp = MCPSimulator(persist_callback=persist)

    mcp.register_tool(
        name="get_crypto_price",
        description=(
            "Get the current real-time market price for a cryptocurrency in USD. "
            "Input: symbol like BTC, ETH, SOL, or BTC/USDT."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Cryptocurrency symbol, e.g. BTC, ETH, BTC/USDT",
                }
            },
            "required": ["symbol"],
        },
        handler=handle_get_price,
    )

    mcp.register_tool(
        name="get_orderbook",
        description="Get the order book (buy/sell depth) for a trading pair.",
        input_schema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Trading pair symbol, e.g. BTC/USDT",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of orders to return",
                    "default": 5,
                },
            },
            "required": ["symbol"],
        },
        handler=handle_get_orderbook,
    )

    mcp.register_tool(
        name="buy_crypto",
        description=(
            "Simulate buying cryptocurrency with USD. Uses real market price. "
            "This is a simulation — no real money is spent."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Cryptocurrency symbol to buy, e.g. BTC, ETH",
                },
                "amount": {
                    "type": "number",
                    "description": "Amount in USD to spend",
                },
            },
            "required": ["symbol", "amount"],
        },
        handler=partial(handle_buy_crypto, user_id),
    )

    mcp.register_tool(
        name="check_balance",
        description="Get the user's wallet balance with current USD values.",
        input_schema={"type": "object", "properties": {}},
        handler=partial(handle_check_balance, user_id),
    )

    mcp.register_tool(
        name="transaction_history",
        description="Get the user's recent transaction history.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of transactions to return",
                    "default": 10,
                }
            },
        },
        handler=partial(handle_transaction_history, user_id),
    )

    return mcp
