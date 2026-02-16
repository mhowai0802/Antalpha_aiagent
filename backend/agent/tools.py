"""
LangChain tools for crypto agent: price, orderbook, buy, balance, transaction history.
"""
from typing import List, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from db.mongo import (
    get_wallet,
    init_wallet,
    update_wallet_buy,
    get_transactions,
)
from mcp_client.ccxt_client import get_ccxt_client


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


def create_tools(user_id: str = "user_default") -> List[BaseTool]:
    """Create LangChain tools bound to a user_id."""

    class GetCryptoPriceTool(BaseTool):
        name: str = "get_crypto_price"
        description: str = (
            "Get the current real-time market price for a cryptocurrency in USD. "
            "Input: symbol like BTC, ETH, SOL, or BTC/USDT. "
            "Price data comes from Binance."
        )
        args_schema: Type[BaseModel] = CryptoPriceInput

        def _run(self, symbol: str) -> str:
            try:
                client = get_ccxt_client()
                ticker = client.get_ticker(symbol)
                return (
                    f"{ticker['symbol']} price info:\n"
                    f"  Current: ${ticker['last']:,.2f}\n"
                    f"  Bid: ${ticker['bid']:,.2f} | Ask: ${ticker['ask']:,.2f}\n"
                    f"  24h High: ${ticker['high']:,.2f} | Low: ${ticker['low']:,.2f}\n"
                    f"  24h Volume: {ticker['volume']:,.2f}"
                )
            except Exception as e:
                return f"Error: {str(e)}"

    class GetOrderbookTool(BaseTool):
        name: str = "get_orderbook"
        description: str = (
            "Get the order book (buy/sell depth) for a trading pair. "
            "Shows current market bids and asks."
        )
        args_schema: Type[BaseModel] = CryptoOrderbookInput

        def _run(self, symbol: str, limit: int = 5) -> str:
            try:
                client = get_ccxt_client()
                ob = client.get_orderbook(symbol, limit)
                lines = [f"Order book for {ob['symbol']}:\n"]
                lines.append("Asks (sell):")
                for ask in ob["asks"][:limit]:
                    lines.append(f"  ${ask[0]:,.2f} x {ask[1]:,.8f}")
                lines.append("\nBids (buy):")
                for bid in ob["bids"][:limit]:
                    lines.append(f"  ${bid[0]:,.2f} x {bid[1]:,.8f}")
                return "\n".join(lines)
            except Exception as e:
                return f"Error: {str(e)}"

    class BuyCryptoTool(BaseTool):
        name: str = "buy_crypto"
        description: str = (
            "Simulate buying cryptocurrency with USD. Uses real market price from Binance. "
            "Input: symbol (e.g. BTC, ETH) and amount in USD. "
            "This is a simulation - no real money is spent."
        )
        args_schema: Type[BaseModel] = CryptoBuyInput

        def _run(self, symbol: str, amount: float) -> str:
            try:
                if amount <= 0:
                    return "Error: Amount must be greater than 0"
                client = get_ccxt_client()
                ticker = client.get_ticker(symbol)
                price = ticker["last"]
                base_symbol = symbol.split("/")[0] if "/" in symbol else symbol.upper()
                crypto_amount = amount / price
                err = update_wallet_buy(user_id, base_symbol, crypto_amount, amount, price)
                if err:
                    return err
                return (
                    f"Simulated buy successful!\n"
                    f"  Bought {crypto_amount:.8f} {base_symbol}\n"
                    f"  Spent: ${amount:,.2f} USD\n"
                    f"  Price: ${price:,.2f} per {base_symbol}"
                )
            except Exception as e:
                return f"Error: {str(e)}"

    class CheckBalanceTool(BaseTool):
        name: str = "check_balance"
        description: str = "Get the user's wallet balance. Shows all assets with current USD values."
        args_schema: Type[BaseModel] = CryptoBalanceInput

        def _run(self, **kwargs) -> str:
            try:
                init_wallet(user_id)
                wallet = get_wallet(user_id)
                client = get_ccxt_client()
                lines = ["Wallet balance:"]
                total_usd = wallet.get("USD", 0.0)
                for asset, balance in wallet.items():
                    if balance <= 0:
                        continue
                    if asset == "USD":
                        lines.append(f"  {asset}: ${balance:,.2f}")
                    else:
                        try:
                            ticker = client.get_ticker(f"{asset}/USDT")
                            price = ticker["last"]
                            usd_val = balance * price
                            total_usd += usd_val
                            lines.append(f"  {asset}: {balance:.8f} (~${usd_val:,.2f})")
                        except Exception:
                            lines.append(f"  {asset}: {balance:.8f}")
                lines.append(f"\nTotal value: ~${total_usd:,.2f} USD")
                return "\n".join(lines)
            except Exception as e:
                return f"Error: {str(e)}"

    class TransactionHistoryTool(BaseTool):
        name: str = "transaction_history"
        description: str = (
            "Get the user's recent transaction history. "
            "Shows buys with symbol, amount, price, and timestamp."
        )
        args_schema: Type[BaseModel] = TransactionHistoryInput

        def _run(self, limit: int = 10) -> str:
            try:
                txs = get_transactions(user_id, limit)
                if not txs:
                    return "No transactions yet."
                lines = ["Recent transactions:"]
                for t in txs:
                    lines.append(
                        f"  {t['type']} {t['amount']:.8f} {t['symbol']} @ ${t['price']:,.2f} "
                        f"(${t['usd_value']:,.2f}) - {t['timestamp']}"
                    )
                return "\n".join(lines)
            except Exception as e:
                return f"Error: {str(e)}"

    return [
        GetCryptoPriceTool(),
        GetOrderbookTool(),
        BuyCryptoTool(),
        CheckBalanceTool(),
        TransactionHistoryTool(),
    ]
