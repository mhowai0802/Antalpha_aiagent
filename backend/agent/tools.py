"""
LangChain tools for crypto agent.
Each tool delegates to the MCP simulator so every call is logged as
a JSON-RPC request/response pair visible to the frontend.
"""
from typing import Any, List, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from mcp_server.simulator import MCPSimulator


# ── Input schemas (unchanged) ────────────────────────────────────

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


# ── Helper to extract text from an MCP response ─────────────────

def _mcp_text(resp: dict) -> str:
    """Pull the text content out of an MCP JSON-RPC response."""
    if "error" in resp:
        return f"Error: {resp['error']['message']}"
    return resp["result"]["content"][0]["text"]


# ── Tool factory ─────────────────────────────────────────────────

def create_tools(user_id: str = "user_default",
                 mcp_server: MCPSimulator | None = None) -> List[BaseTool]:
    """Create LangChain tools that route through the MCP simulator."""

    class GetCryptoPriceTool(BaseTool):
        name: str = "get_crypto_price"
        description: str = (
            "Get the current real-time market price for a cryptocurrency in USD. "
            "Input: symbol like BTC, ETH, SOL, or BTC/USDT. "
            "Price data comes from the exchange."
        )
        args_schema: Type[BaseModel] = CryptoPriceInput
        _mcp: Any = None

        def _run(self, symbol: str) -> str:
            if self._mcp:
                return _mcp_text(self._mcp.call_tool("get_crypto_price", {"symbol": symbol}))
            from mcp_server.handlers import handle_get_price
            return handle_get_price(symbol)

    class GetOrderbookTool(BaseTool):
        name: str = "get_orderbook"
        description: str = (
            "Get the order book (buy/sell depth) for a trading pair. "
            "Shows current market bids and asks."
        )
        args_schema: Type[BaseModel] = CryptoOrderbookInput
        _mcp: Any = None

        def _run(self, symbol: str, limit: int = 5) -> str:
            if self._mcp:
                return _mcp_text(self._mcp.call_tool("get_orderbook", {"symbol": symbol, "limit": limit}))
            from mcp_server.handlers import handle_get_orderbook
            return handle_get_orderbook(symbol, limit)

    class BuyCryptoTool(BaseTool):
        name: str = "buy_crypto"
        description: str = (
            "Simulate buying cryptocurrency with USD. Uses real market price. "
            "Input: symbol (e.g. BTC, ETH) and amount in USD. "
            "This is a simulation - no real money is spent."
        )
        args_schema: Type[BaseModel] = CryptoBuyInput
        _mcp: Any = None

        def _run(self, symbol: str, amount: float) -> str:
            if self._mcp:
                return _mcp_text(self._mcp.call_tool("buy_crypto", {"symbol": symbol, "amount": amount}))
            from mcp_server.handlers import handle_buy_crypto
            return handle_buy_crypto(user_id, symbol, amount)

    class CheckBalanceTool(BaseTool):
        name: str = "check_balance"
        description: str = "Get the user's wallet balance. Shows all assets with current USD values."
        args_schema: Type[BaseModel] = CryptoBalanceInput
        _mcp: Any = None

        def _run(self, **kwargs) -> str:
            if self._mcp:
                return _mcp_text(self._mcp.call_tool("check_balance", {}))
            from mcp_server.handlers import handle_check_balance
            return handle_check_balance(user_id)

    class TransactionHistoryTool(BaseTool):
        name: str = "transaction_history"
        description: str = (
            "Get the user's recent transaction history. "
            "Shows buys with symbol, amount, price, and timestamp."
        )
        args_schema: Type[BaseModel] = TransactionHistoryInput
        _mcp: Any = None

        def _run(self, limit: int = 10) -> str:
            if self._mcp:
                return _mcp_text(self._mcp.call_tool("transaction_history", {"limit": limit}))
            from mcp_server.handlers import handle_transaction_history
            return handle_transaction_history(user_id, limit)

    tools = [
        GetCryptoPriceTool(),
        GetOrderbookTool(),
        BuyCryptoTool(),
        CheckBalanceTool(),
        TransactionHistoryTool(),
    ]

    if mcp_server is not None:
        for t in tools:
            t._mcp = mcp_server

    return tools
