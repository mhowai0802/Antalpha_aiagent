"""
Standalone handler functions for the MCP simulator.
Each function mirrors the logic that was previously inside a LangChain tool's
``_run()`` method, but is a plain function so the MCP simulator can call it.
"""
from mcp_client.ccxt_client import get_ccxt_client
from db.mongo import get_wallet, init_wallet, update_wallet_buy, get_transactions


def handle_get_price(symbol: str) -> str:
    """Fetch real-time price for *symbol* from the exchange."""
    client = get_ccxt_client()
    ticker = client.get_ticker(symbol)
    return (
        f"{ticker['symbol']} price info:\n"
        f"  Current: ${ticker['last']:,.2f}\n"
        f"  Bid: ${ticker['bid']:,.2f} | Ask: ${ticker['ask']:,.2f}\n"
        f"  24h High: ${ticker['high']:,.2f} | Low: ${ticker['low']:,.2f}\n"
        f"  24h Volume: {ticker['volume']:,.2f}"
    )


def handle_get_orderbook(symbol: str, limit: int = 5) -> str:
    """Fetch order-book depth for *symbol*."""
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


def handle_buy_crypto(user_id: str, symbol: str, amount: float) -> str:
    """Simulate buying *amount* USD worth of *symbol*."""
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


def handle_check_balance(user_id: str) -> str:
    """Return the user's current wallet balance with USD values."""
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


def handle_transaction_history(user_id: str, limit: int = 10) -> str:
    """Return recent transaction history for *user_id*."""
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
