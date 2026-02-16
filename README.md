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

## Deploy as Demo (Free Tier)

You can deploy the full app for **$0/month** using Vercel (frontend) + Render (backend) + MongoDB Atlas M0 (database).

### Backend → Render

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) and sign in with GitHub.
3. Click **New → Web Service**, connect this repo.
4. Render will auto-detect `render.yaml` — confirm the settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set the secret environment variables in the Render dashboard:
   - `HKBU_API_KEY` — your HKBU GenAI API key
   - `MONGODB_URI` — your MongoDB Atlas connection string
   - `FRONTEND_URL` — your Vercel URL (set after deploying frontend, e.g. `https://your-app.vercel.app`)
6. Deploy. Note your backend URL (e.g. `https://crypto-agent-backend.onrender.com`).

> **Note**: Render free tier sleeps after 15 min of inactivity. First request after sleep takes ~30-50s to spin up — acceptable for a demo.

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New → Project**, import this repo.
3. Set **Root Directory** to `frontend`.
4. Vercel auto-detects Vite. Confirm:
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - `VITE_API_URL` = your Render backend URL (e.g. `https://crypto-agent-backend.onrender.com`)
6. Deploy. Your demo is live!

### After Both Are Deployed

Go back to Render and set `FRONTEND_URL` to your Vercel URL so CORS works correctly.

## Tech Stack

- **Backend**: FastAPI, LangChain, CCXT, MongoDB, HKBU GenAI (gemini-2.5-flash)
- **Frontend**: React, TypeScript, Vite, Redux Toolkit
