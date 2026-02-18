"""
LangChain tools for crypto agent.
Each tool delegates to the MCP bridge so every call is logged as
a JSON-RPC request/response pair visible to the frontend.

Input Pydantic models are kept for LangChain schema generation.
Tool routing goes through MCPBridge.call_tool().
"""
from typing import Any, List, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from mcp_server.bridge import MCPBridge


# ── Input schemas ─────────────────────────────────────────────────

class CryptoPriceInput(BaseModel):
    """Input for get_crypto_price tool."""
    symbol: str = Field(description="Cryptocurrency symbol, e.g. BTC, ETH, BTC/USDT")


class CryptoOrderbookInput(BaseModel):
    """Input for get_orderbook tool."""
    symbol: str = Field(description="Trading pair symbol, e.g. BTC/USDT")
    limit: int = Field(default=5, description="Number of orders to return")


class CryptoBuyInput(BaseModel):
    """Input for buy_crypto tool."""
    symbol: str = Field(description="Cryptocurrency symbol to buy, e.g. BTC, ETH")
    amount: float = Field(description="Amount in USD to spend")


class CryptoBalanceInput(BaseModel):
    """Input for check_balance tool."""
    pass


class TransactionHistoryInput(BaseModel):
    """Input for transaction_history tool."""
    limit: int = Field(default=10, description="Number of transactions to return")


# ── Helper to extract text from an MCP response ──────────────────

def _mcp_text(resp: dict) -> str:
    """Pull the text content out of an MCP JSON-RPC response."""
    if "error" in resp:
        return f"Error: {resp['error']['message']}"
    return resp["result"]["content"][0]["text"]


# ── Tool specification table ──────────────────────────────────────
# Single table that drives LangChain tool generation.
# Each entry maps to one tool: (name, description, args_schema, arg_keys).

_TOOL_TABLE = [
    {
        "name": "get_crypto_price",
        "description": (
            "Get the current real-time market price for a cryptocurrency in USD. "
            "Input: symbol like BTC, ETH, SOL, or BTC/USDT. "
            "Price data comes from the exchange."
        ),
        "args_schema": CryptoPriceInput,
        "arg_keys": ["symbol"],
    },
    {
        "name": "get_orderbook",
        "description": (
            "Get the order book (buy/sell depth) for a trading pair. "
            "Shows current market bids and asks."
        ),
        "args_schema": CryptoOrderbookInput,
        "arg_keys": ["symbol", "limit"],
    },
    {
        "name": "buy_crypto",
        "description": (
            "Simulate buying cryptocurrency with USD. Uses real market price. "
            "Input: symbol (e.g. BTC, ETH) and amount in USD. "
            "This is a simulation - no real money is spent."
        ),
        "args_schema": CryptoBuyInput,
        "arg_keys": ["symbol", "amount"],
    },
    {
        "name": "check_balance",
        "description": "Get the user's wallet balance. Shows all assets with current USD values.",
        "args_schema": CryptoBalanceInput,
        "arg_keys": [],
    },
    {
        "name": "transaction_history",
        "description": (
            "Get the user's recent transaction history. "
            "Shows buys with symbol, amount, price, and timestamp."
        ),
        "args_schema": TransactionHistoryInput,
        "arg_keys": ["limit"],
    },
]


# ── Tool factory ──────────────────────────────────────────────────

def _make_tool(spec: dict, mcp_bridge: MCPBridge | None) -> BaseTool:
    """
    Dynamically create a LangChain BaseTool subclass from a spec dict.
    The tool routes calls through the MCP bridge for logging.
    """
    tool_name = spec["name"]
    tool_desc = spec["description"]
    tool_schema = spec["args_schema"]
    arg_keys = spec["arg_keys"]

    class _DynamicTool(BaseTool):
        name: str = tool_name
        description: str = tool_desc
        args_schema: Type[BaseModel] = tool_schema
        _mcp: Any = None

        def _run(self, **kwargs) -> str:
            args = {k: kwargs[k] for k in arg_keys if k in kwargs}
            if self._mcp:
                return _mcp_text(self._mcp.call_tool(tool_name, args))
            # Fallback: call handler directly (no logging)
            from mcp_server.handlers import (
                handle_get_price,
                handle_get_orderbook,
                handle_buy_crypto,
                handle_check_balance,
                handle_transaction_history,
            )
            from mcp_server.utils import format_for_display
            handler_map = {
                "get_crypto_price": handle_get_price,
                "get_orderbook": handle_get_orderbook,
                "buy_crypto": handle_buy_crypto,
                "check_balance": handle_check_balance,
                "transaction_history": handle_transaction_history,
            }
            return format_for_display(handler_map[tool_name](**args))

    tool = _DynamicTool()
    tool._mcp = mcp_bridge
    return tool


def create_tools(
    user_id: str = "user_default",
    mcp_server: MCPBridge | None = None,
) -> List[BaseTool]:
    """Create LangChain tools that route through the MCP bridge."""
    return [_make_tool(spec, mcp_server) for spec in _TOOL_TABLE]
