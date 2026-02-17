"""
FastMCP server — single source of truth for all tool definitions.

Uses @mcp.tool() decorators following the Binance MCP server pattern.
Each tool is a thin wrapper that delegates to a handler in handlers.py.

This module serves two purposes:
1. Canonical tool definitions (name, description, schema via type hints)
2. Real MCP server that can be mounted via SSE for external MCP clients
"""
import logging
from typing import Any, Dict, Optional

from fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="crypto-agent",
    version="1.0.0",
    instructions="""
    Cryptocurrency trading assistant MCP server.

    AVAILABLE TOOLS:

    Market Data:
    - get_crypto_price: Get current price for a cryptocurrency
    - get_orderbook: Get order book (buy/sell depth) for a trading pair

    Trading:
    - buy_crypto: Simulate buying cryptocurrency with USD (no real money)

    Account:
    - check_balance: Get wallet balance with current USD values
    - transaction_history: Get recent transaction history

    All market data comes from live exchange APIs via CCXT.
    Trading operations are simulated — no real money is involved.
    """,
)


# ── Tool definitions ──────────────────────────────────────────────
# Each @mcp.tool() function is the canonical definition.
# The FastMCP SDK auto-generates JSON Schema from the type hints.

@mcp.tool()
def get_crypto_price(symbol: str) -> Dict[str, Any]:
    """
    Get the current real-time market price for a cryptocurrency in USD.
    Input: symbol like BTC, ETH, SOL, or BTC/USDT.
    Price data comes from the exchange via CCXT.
    """
    logger.info(f"Tool called: get_crypto_price with symbol={symbol}")
    from mcp_server.handlers import handle_get_price
    return handle_get_price(symbol)


@mcp.tool()
def get_orderbook(symbol: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get the order book (buy/sell depth) for a trading pair.
    Shows current market bids and asks from the exchange.
    """
    logger.info(f"Tool called: get_orderbook with symbol={symbol}, limit={limit}")
    from mcp_server.handlers import handle_get_orderbook
    return handle_get_orderbook(symbol, limit)


@mcp.tool()
def buy_crypto(
    symbol: str,
    amount: float,
    user_id: str = "user_default",
) -> Dict[str, Any]:
    """
    Simulate buying cryptocurrency with USD. Uses real market price.
    This is a simulation — no real money is spent.
    """
    logger.info(f"Tool called: buy_crypto with symbol={symbol}, amount={amount}")
    from mcp_server.handlers import handle_buy_crypto
    return handle_buy_crypto(user_id, symbol, amount)


@mcp.tool()
def check_balance(user_id: str = "user_default") -> Dict[str, Any]:
    """
    Get the user's wallet balance with current USD values.
    Shows all assets and their approximate USD value.
    """
    logger.info(f"Tool called: check_balance for user={user_id}")
    from mcp_server.handlers import handle_check_balance
    return handle_check_balance(user_id)


@mcp.tool()
def transaction_history(
    limit: int = 10,
    user_id: str = "user_default",
) -> Dict[str, Any]:
    """
    Get the user's recent transaction history.
    Shows buys with symbol, amount, price, and timestamp.
    """
    logger.info(f"Tool called: transaction_history for user={user_id}, limit={limit}")
    from mcp_server.handlers import handle_transaction_history
    return handle_transaction_history(user_id, limit)


# ── Tool specifications (used by the bridge for JSON-RPC logging) ─

TOOL_SPECS = [
    {
        "name": "get_crypto_price",
        "description": (
            "Get the current real-time market price for a cryptocurrency in USD. "
            "Input: symbol like BTC, ETH, SOL, or BTC/USDT."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Cryptocurrency symbol, e.g. BTC, ETH, BTC/USDT",
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_orderbook",
        "description": "Get the order book (buy/sell depth) for a trading pair.",
        "inputSchema": {
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
    },
    {
        "name": "buy_crypto",
        "description": (
            "Simulate buying cryptocurrency with USD. Uses real market price. "
            "This is a simulation — no real money is spent."
        ),
        "inputSchema": {
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
    },
    {
        "name": "check_balance",
        "description": "Get the user's wallet balance with current USD values.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "transaction_history",
        "description": "Get the user's recent transaction history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of transactions to return",
                    "default": 10,
                }
            },
        },
    },
]
