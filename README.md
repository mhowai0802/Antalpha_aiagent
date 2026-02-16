# Crypto Trading AI Agent

Full-stack app: React frontend + Python FastAPI backend. Simulated crypto trading with real Binance prices.
Uses LangChain, CCXT, MongoDB, and HKBU GenAI API.

## Features

- Real-time crypto prices from Binance
- Simulated wallet and transactions (no real money)
- AI agent chat (English)
- Wallet balance and transaction history

## Project Structure

```
Antalpha_aiagent/
├── backend/          # FastAPI, LangChain, CCXT, MongoDB
├── frontend/         # React, Vite, Redux
└── README.md
```

## Backend Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in:

- `HKBU_API_KEY` — your HKBU GenAI API key
- `MONGODB_URI` — MongoDB Atlas connection string
- `MONGODB_DB` — database name (default: crypto_agent)

### 4. Run

```bash
uvicorn main:app --reload --port 8000
```

API: http://localhost:8000

- `POST /chat` — chat with agent
- `GET /balance/{user_id}` — wallet balance
- `GET /transactions/{user_id}` — transaction history
- `GET /health` — health check

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Testing the Backend

### Quick test (no server needed)

```bash
cd backend
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
python test_backend.py
```

Tests: `GET /health`, `GET /balance`, `GET /transactions`, `POST /chat`.

### Live test (server must be running)

```bash
# Terminal 1: start server
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: run tests against live server
cd backend && python test_backend.py --live
```

### Troubleshooting

- **MongoDB SSL certificate error** (macOS): Run `Applications/Python 3.x/Install Certificates.command` or install certifi: `pip install certifi` and set `SSL_CERT_FILE` to the certifi bundle.
- **Chat test fails**: Ensure `HKBU_API_KEY` is set in `.env`.

## API Examples

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the price of BTC?", "user_id": "user_default"}'
```

### Balance

```bash
curl http://localhost:8000/balance/user_default
```

### Transactions

```bash
curl http://localhost:8000/transactions/user_default
```

## Tech Stack

- **Backend**: FastAPI, LangChain, CCXT, MongoDB, HKBU GenAI (gemini-2.5-flash)
- **Frontend**: React, TypeScript, Vite, Redux Toolkit
