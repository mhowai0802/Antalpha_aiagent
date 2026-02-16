"""
MongoDB operations for wallet and transaction persistence.
"""
import os
from datetime import datetime
from typing import Optional

import certifi
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# Default user ID for single-user demo
DEFAULT_USER_ID = "user_default"
INITIAL_USD = 10000.0

_client: Optional[MongoClient] = None


def get_db() -> Database:
    """Connect to MongoDB Atlas and return database handle."""
    global _client
    uri = os.getenv("MONGODB_URI", "")
    db_name = os.getenv("MONGODB_DB", "crypto_agent")
    if not uri:
        raise ValueError("MONGODB_URI environment variable is required")
    if _client is None:
        _client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where(),
        )
    return _client[db_name]


def _wallets_collection() -> Collection:
    return get_db()["wallets"]


def _transactions_collection() -> Collection:
    return get_db()["transactions"]


def init_wallet(user_id: str = DEFAULT_USER_ID) -> dict:
    """
    Create wallet with $10,000 USD if not exists.
    Returns the wallet document.
    """
    coll = _wallets_collection()
    now = datetime.utcnow().isoformat()
    coll.update_one(
        {"_id": user_id},
        {
            "$setOnInsert": {
                "assets": {"USD": INITIAL_USD},
                "created_at": now,
                "updated_at": now,
            }
        },
        upsert=True,
    )
    return coll.find_one({"_id": user_id})


def get_wallet(user_id: str = DEFAULT_USER_ID) -> dict:
    """
    Read current wallet balances.
    Returns dict of asset -> balance.
    """
    doc = _wallets_collection().find_one({"_id": user_id})
    if doc is None:
        init_wallet(user_id)
        return {"USD": INITIAL_USD}
    return doc.get("assets", {})


def update_wallet_buy(
    user_id: str,
    symbol: str,
    crypto_amount: float,
    usd_amount: float,
    price: float,
) -> Optional[str]:
    """
    Deduct USD, add crypto, insert transaction record.
    Uses atomic $inc for safe balance updates.
    Returns None on success, error message on failure.
    """
    coll = _wallets_collection()
    doc = coll.find_one({"_id": user_id})
    if doc is None:
        init_wallet(user_id)
        doc = coll.find_one({"_id": user_id})

    assets = doc.get("assets", {})
    usd_balance = assets.get("USD", 0.0)

    if usd_balance < usd_amount:
        return f"Insufficient balance. Need ${usd_amount:,.2f}, have ${usd_balance:,.2f}"

    now = datetime.utcnow().isoformat()

    # Atomic update: deduct USD, add crypto
    coll.update_one(
        {"_id": user_id},
        {
            "$inc": {
                "assets.USD": -usd_amount,
                f"assets.{symbol}": crypto_amount,
            },
            "$set": {"updated_at": now},
        },
    )

    # Insert transaction record
    _transactions_collection().insert_one(
        {
            "user_id": user_id,
            "type": "BUY",
            "symbol": symbol,
            "amount": crypto_amount,
            "price": price,
            "usd_value": usd_amount,
            "timestamp": now,
        }
    )

    return None


def get_transactions(user_id: str = DEFAULT_USER_ID, limit: int = 20) -> list:
    """Fetch recent transaction history."""
    cursor = (
        _transactions_collection()
        .find({"user_id": user_id})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return list(cursor)
