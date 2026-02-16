"""
CCXT client wrapper for fetching real Binance public market data.
No API key required for public endpoints.
"""
import os
from typing import Any, Dict, Optional

import ccxt


class CCXTClient:
    """CCXT client for Binance public data."""

    def __init__(self, exchange_name: Optional[str] = None):
        exchange_name = exchange_name or os.getenv("DEFAULT_EXCHANGE", "binance")
        self.exchange_name = exchange_name.lower()
        exchange_class = getattr(ccxt, self.exchange_name, None)
        if exchange_class is None:
            raise ValueError(f"Unsupported exchange: {self.exchange_name}")
        self.exchange = exchange_class(
            {"enableRateLimit": True, "options": {"defaultType": "spot"}}
        )

    def _normalize_symbol(self, symbol: str) -> str:
        """Ensure symbol has /USDT format."""
        if "/" not in symbol:
            return f"{symbol.upper()}/USDT"
        return symbol

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch ticker (price, bid, ask, volume, etc.) for a symbol."""
        symbol = self._normalize_symbol(symbol)
        ticker = self.exchange.fetch_ticker(symbol)
        return {
            "symbol": symbol,
            "last": ticker.get("last", 0),
            "bid": ticker.get("bid", 0),
            "ask": ticker.get("ask", 0),
            "high": ticker.get("high", 0),
            "low": ticker.get("low", 0),
            "volume": ticker.get("volume", 0),
            "timestamp": ticker.get("timestamp", 0),
            "datetime": ticker.get("datetime", ""),
        }

    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        ticker = self.get_ticker(symbol)
        return ticker["last"]

    def get_orderbook(self, symbol: str, limit: int = 5) -> Dict[str, Any]:
        """Fetch order book (bids/asks) for a symbol."""
        symbol = self._normalize_symbol(symbol)
        orderbook = self.exchange.fetch_order_book(symbol, limit)
        return {
            "symbol": symbol,
            "bids": orderbook.get("bids", []),
            "asks": orderbook.get("asks", []),
            "timestamp": orderbook.get("timestamp", 0),
        }

    def close(self) -> None:
        """Close exchange connection."""
        if self.exchange:
            self.exchange.close()


_ccxt_client: Optional[CCXTClient] = None


def get_ccxt_client() -> CCXTClient:
    """Get singleton CCXT client instance."""
    global _ccxt_client
    if _ccxt_client is None:
        _ccxt_client = CCXTClient()
    return _ccxt_client
