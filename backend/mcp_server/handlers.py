"""
Standalone handler functions for the MCP server.
Each handler returns a structured Dict response following the
Binance MCP server pattern: {success, data, error, timestamp}.
"""
import logging
from typing import Any, Dict

from mcp_client.ccxt_client import get_ccxt_client
from db.mongo import get_wallet, init_wallet, update_wallet_buy, get_transactions
from mcp_server.utils import (
    create_success_response,
    create_error_response,
    validate_symbol,
    validate_positive_number,
    rate_limited,
    exchange_rate_limiter,
)

logger = logging.getLogger(__name__)


@rate_limited(exchange_rate_limiter)
def handle_get_price(symbol: str) -> Dict[str, Any]:
    """Fetch real-time price for *symbol* from the exchange."""
    logger.info(f"Handler called: handle_get_price with symbol={symbol}")
    try:
        normalized = validate_symbol(symbol)
        client = get_ccxt_client()
        ticker = client.get_ticker(normalized)
        return create_success_response(
            data={
                "symbol": ticker["symbol"],
                "last": ticker["last"],
                "bid": ticker["bid"],
                "ask": ticker["ask"],
                "high": ticker["high"],
                "low": ticker["low"],
                "volume": ticker["volume"],
            },
            metadata={"source": "ccxt", "endpoint": "get_ticker"},
        )
    except ValueError as e:
        logger.warning(f"Validation error for symbol '{symbol}': {e}")
        return create_error_response("validation_error", str(e))
    except Exception as e:
        logger.error(f"Exchange error in handle_get_price: {e}")
        return create_error_response("exchange_error", str(e))


@rate_limited(exchange_rate_limiter)
def handle_get_orderbook(symbol: str, limit: int = 5) -> Dict[str, Any]:
    """Fetch order-book depth for *symbol*."""
    logger.info(f"Handler called: handle_get_orderbook with symbol={symbol}, limit={limit}")
    try:
        normalized = validate_symbol(symbol)
        client = get_ccxt_client()
        ob = client.get_orderbook(normalized, limit)
        return create_success_response(
            data={
                "symbol": ob["symbol"],
                "asks": [{"price": a[0], "quantity": a[1]} for a in ob["asks"][:limit]],
                "bids": [{"price": b[0], "quantity": b[1]} for b in ob["bids"][:limit]],
            },
            metadata={"source": "ccxt", "endpoint": "get_orderbook", "limit": limit},
        )
    except ValueError as e:
        logger.warning(f"Validation error for orderbook '{symbol}': {e}")
        return create_error_response("validation_error", str(e))
    except Exception as e:
        logger.error(f"Exchange error in handle_get_orderbook: {e}")
        return create_error_response("exchange_error", str(e))


@rate_limited(exchange_rate_limiter)
def handle_buy_crypto(user_id: str, symbol: str, amount: float) -> Dict[str, Any]:
    """Simulate buying *amount* USD worth of *symbol*."""
    logger.info(f"Handler called: handle_buy_crypto user={user_id}, symbol={symbol}, amount={amount}")
    try:
        validate_positive_number(amount, "amount")
        normalized = validate_symbol(symbol)
        client = get_ccxt_client()
        ticker = client.get_ticker(normalized)
        price = ticker["last"]
        base_symbol = normalized.split("/")[0] if "/" in normalized else normalized
        crypto_amount = amount / price

        err = update_wallet_buy(user_id, base_symbol, crypto_amount, amount, price)
        if err:
            return create_error_response("insufficient_balance", err)

        return create_success_response(
            data={
                "action": "buy",
                "symbol": base_symbol,
                "crypto_amount": crypto_amount,
                "usd_spent": amount,
                "price": price,
            },
            metadata={"simulated": True},
        )
    except ValueError as e:
        logger.warning(f"Validation error in buy_crypto: {e}")
        return create_error_response("validation_error", str(e))
    except Exception as e:
        logger.error(f"Error in handle_buy_crypto: {e}")
        return create_error_response("exchange_error", str(e))


def handle_check_balance(user_id: str) -> Dict[str, Any]:
    """Return the user's current wallet balance with USD values."""
    logger.info(f"Handler called: handle_check_balance for user={user_id}")
    try:
        init_wallet(user_id)
        wallet = get_wallet(user_id)
        client = get_ccxt_client()

        assets = []
        total_usd = wallet.get("USD", 0.0)

        for asset, balance in wallet.items():
            if balance <= 0:
                continue
            if asset == "USD":
                assets.append({"asset": asset, "balance": balance, "usd_value": balance})
            else:
                try:
                    ticker = client.get_ticker(f"{asset}/USDT")
                    price = ticker["last"]
                    usd_val = balance * price
                    total_usd += usd_val
                    assets.append({
                        "asset": asset,
                        "balance": balance,
                        "price": price,
                        "usd_value": usd_val,
                    })
                except Exception:
                    assets.append({"asset": asset, "balance": balance, "usd_value": None})

        return create_success_response(
            data={"assets": assets, "total_usd": total_usd},
        )
    except Exception as e:
        logger.error(f"Error in handle_check_balance: {e}")
        return create_error_response("tool_error", str(e))


def handle_transaction_history(user_id: str, limit: int = 10) -> Dict[str, Any]:
    """Return recent transaction history for *user_id*."""
    logger.info(f"Handler called: handle_transaction_history for user={user_id}, limit={limit}")
    try:
        txs = get_transactions(user_id, limit)
        tx_list = []
        for t in txs:
            tx_list.append({
                "type": t["type"],
                "symbol": t["symbol"],
                "amount": t["amount"],
                "price": t["price"],
                "usd_value": t["usd_value"],
                "timestamp": t["timestamp"],
            })
        return create_success_response(
            data={"transactions": tx_list, "count": len(tx_list)},
        )
    except Exception as e:
        logger.error(f"Error in handle_transaction_history: {e}")
        return create_error_response("tool_error", str(e))
