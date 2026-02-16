#!/bin/bash
# Manual API tests using curl. Run with backend server at http://localhost:8000
BASE=${1:-http://localhost:8000}
echo "Testing $BASE"
echo ""
echo "1. GET /health"
curl -s "$BASE/health" | python3 -m json.tool
echo ""
echo "2. GET /balance/user_default"
curl -s "$BASE/balance/user_default" | python3 -m json.tool
echo ""
echo "3. GET /transactions/user_default"
curl -s "$BASE/transactions/user_default" | python3 -m json.tool
echo ""
echo "4. POST /chat"
curl -s -X POST "$BASE/chat" -H "Content-Type: application/json" \
  -d '{"message":"What is the price of BTC?","user_id":"user_default"}' | python3 -m json.tool
