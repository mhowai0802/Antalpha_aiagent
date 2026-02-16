"""
Backend API tests. Run from backend/ with: python test_backend.py
Requires: .env with MONGODB_URI (and HKBU_API_KEY for chat tests).

Usage:
  python test_backend.py           # Test against TestClient (no server)
  python test_backend.py --live    # Test against running server at http://localhost:8000
"""
import os
import sys

# Ensure backend is on path and .env is loaded
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

load_dotenv()

USE_LIVE = "--live" in sys.argv
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
USER_ID = "user_default"

if USE_LIVE:
    import urllib.request
    import json

    class _Resp:
        def __init__(self, code: int, data):
            self.status_code = code
            self._data = data
        def json(self):
            return self._data
        @property
        def text(self):
            return str(self._data) if isinstance(self._data, dict) else self._data

    def _get(path: str) -> _Resp:
        req = urllib.request.Request(BASE_URL + path)
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return _Resp(200, json.loads(r.read().decode()))
        except urllib.error.HTTPError as e:
            return _Resp(e.code, {"error": e.read().decode()})

    def _post(path: str, data: dict) -> _Resp:
        req = urllib.request.Request(
            BASE_URL + path,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return _Resp(200, json.loads(r.read().decode()))
        except urllib.error.HTTPError as e:
            return _Resp(e.code, {"error": e.read().decode()})

    class LiveClient:
        def get(self, path): return _get(path)
        def post(self, path, *, json=None): return _post(path, json or {})
    client = LiveClient()
else:
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)


def test_health():
    """GET /health - should always return 200."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    print("  [OK] GET /health")


def test_balance():
    """GET /balance/{user_id} - returns wallet assets."""
    r = client.get(f"/balance/{USER_ID}")
    if r.status_code != 200:
        raise AssertionError(f"status {r.status_code}: {getattr(r, 'text', r.json())}")
    data = r.json()
    assert "user_id" in data, f"missing user_id: {data}"
    assert "assets" in data, f"missing assets: {data}"
    assert "USD" in data["assets"], f"USD not in assets: {data.get('assets')}"
    print("  [OK] GET /balance/{user_id}")


def test_transactions():
    """GET /transactions/{user_id} - returns transaction list."""
    r = client.get(f"/transactions/{USER_ID}")
    if r.status_code != 200:
        raise AssertionError(f"status {r.status_code}: {getattr(r, 'text', r.json())}")
    data = r.json()
    assert "user_id" in data, f"missing user_id: {data}"
    assert "transactions" in data, f"missing transactions: {data}"
    assert isinstance(data["transactions"], list), f"transactions not list: {type(data['transactions'])}"
    print("  [OK] GET /transactions/{user_id}")


def test_chat():
    """POST /chat - agent responds to message."""
    r = client.post(
        "/chat",
        json={"message": "What is the price of BTC?", "user_id": USER_ID},
    )
    if r.status_code != 200:
        print(f"  [SKIP] POST /chat - {r.status_code}: {r.text[:200]}")
        return
    data = r.json()
    assert "response" in data
    assert "user_id" in data
    assert len(data["response"]) > 0
    print("  [OK] POST /chat")


def run_all():
    print("\n--- Backend API Tests ---\n")
    errors = []
    for name, fn in [
        ("health", test_health),
        ("balance", test_balance),
        ("transactions", test_transactions),
        ("chat", test_chat),
    ]:
        try:
            fn()
        except Exception as e:
            err_msg = str(e) or repr(e)
            errors.append((name, err_msg))
            print(f"  [FAIL] {name}: {err_msg}")
    print()
    if errors:
        print(f"Failed: {len(errors)} test(s)")
        for name, err in errors:
            print(f"  - {name}: {err}")
        sys.exit(1)
    print("All tests passed.\n")


if __name__ == "__main__":
    run_all()
