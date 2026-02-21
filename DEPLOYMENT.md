# Deployment Guide

Deploy the Crypto Trading AI Agent for **$0/month** using free-tier services.

## Architecture

```
┌─────────────┐     HTTPS      ┌──────────────────────────────────────┐
│   Browser    │ ──────────────▶│  Vercel (Free)                       │
│             │                │  React static: Chat, Wallet,          │
└─────────────┘                │  Transactions, MCP Inspector, Arch    │
                               └────────────────┬─────────────────────┘
                                                │ VITE_API_URL
                                                ▼
                               ┌──────────────────────────────────────┐
                               │  Render (Free)                       │
                               │  FastAPI + LangChain Agent            │
                               │  + MCP Simulator (JSON-RPC logging)   │
                               └──┬──────────┬──────────┬─────────────┘
                                  │          │          │
                     ┌────────────┘          │          └────────────┐
                     ▼                       ▼                       ▼
              ┌─────────────┐   ┌────────────────────┐   ┌──────────────┐
              │ Kraken API  │   │ MongoDB Atlas M0   │   │ HKBU GenAI   │
              │ (prices via │   │ - wallets           │   │ API (LLM)    │
              │  CCXT)      │   │ - transactions      │   │ Gemini 2.5   │
              └─────────────┘   │ - mcp_logs          │   └──────────────┘
                                └────────────────────┘
```

| Component | Platform | Tier | Cost |
|-----------|----------|------|------|
| Frontend | Vercel | Hobby (free) | $0 |
| Backend + MCP Simulator | Render | Free web service | $0 |
| Database | MongoDB Atlas | M0 (free) | $0 |
| AI Model | HKBU GenAI API | University-provided | $0 |
| Market Data | Kraken public API | No key needed | $0 |

## Prerequisites

- GitHub account with this repo pushed
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account with a free M0 cluster
- HKBU GenAI API key
- (Optional) [Render CLI](https://render.com/docs/cli) and [Vercel CLI](https://vercel.com/docs/cli)

## Step 1: Deploy Backend on Render

### Via Dashboard (Recommended for first time)

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New > Blueprint**.
3. Connect the `Antalpha_aiagent` GitHub repo.
4. Render detects `render.yaml` and shows the service configuration. Click **Apply**.
5. Set the **secret** environment variables in the Render dashboard:

   | Variable | Value | Notes |
   |----------|-------|-------|
   | `HKBU_API_KEY` | `your-api-key` | HKBU GenAI API key |
   | `MONGODB_URI` | `mongodb+srv://...` | MongoDB Atlas connection string |
   | `FRONTEND_URL` | _(set after Step 2)_ | Your Vercel URL for CORS |

   The following are pre-configured in `render.yaml` (no action needed):

   | Variable | Default Value |
   |----------|---------------|
   | `HKBU_MODEL` | `gemini-2.5-flash` |
   | `HKBU_BASE_URL` | `https://genai.hkbu.edu.hk/api/v0/rest` |
   | `MONGODB_DB` | `crypto_agent` |
   | `DEFAULT_EXCHANGE` | `kraken` |
   | `PYTHON_VERSION` | `3.11.11` |

6. Click **Deploy Blueprint**.
7. Wait 3-5 minutes for the build and deployment to complete.
8. Note your backend URL: `https://<service-name>.onrender.com`
9. Verify: `curl https://<service-name>.onrender.com/health` should return `{"status":"ok"}`

### Via CLI (subsequent deploys)

```bash
brew install render
render login
render deploys create <service-id> --wait
```

## Step 2: Deploy Frontend on Vercel

### Via Dashboard (Recommended for first time)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New > Project**, import the `Antalpha_aiagent` repo.
3. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable:

   | Variable | Value |
   |----------|-------|
   | `VITE_API_URL` | Your Render backend URL (e.g. `https://crypto-agent-backend-oyyf.onrender.com`) |

5. Click **Deploy**.
6. Note your frontend URL: `https://<project-name>.vercel.app`

### Via CLI

```bash
npm install -g vercel
vercel login
cd frontend
vercel deploy --prod
```

## Step 3: Connect Frontend and Backend

After both are deployed, go back to Render and set the `FRONTEND_URL` environment variable:

```
FRONTEND_URL = https://<your-project>.vercel.app
```

Then trigger a redeploy on Render (or it will auto-deploy on next git push).

This enables CORS so the frontend can make API calls to the backend. The backend also
has a regex rule that allows all `*.vercel.app` origins, so preview deployments work too.

## Step 4: Verify Everything Works

```bash
# Backend health check
curl https://<backend>.onrender.com/health
# Expected: {"status":"ok"}

# Backend balance check
curl https://<backend>.onrender.com/balance/user_default
# Expected: {"user_id":"user_default","assets":{"USD":10000.0}}

# Backend chat test (response now includes agent steps + MCP logs)
curl -X POST https://<backend>.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the price of BTC?", "user_id": "user_default"}'
# Expected: {"response":"...","user_id":"user_default","steps":[{"tool":"get_crypto_price",...}]}

# MCP log — live (current session)
curl https://<backend>.onrender.com/mcp-log/user_default?source=live
# Expected: {"mcp_calls":[...]}

# MCP log — history (from MongoDB, paginated)
curl https://<backend>.onrender.com/mcp-log/user_default?source=history&limit=10&skip=0
# Expected: {"mcp_calls":[...]}

# Clear MCP history
curl -X DELETE https://<backend>.onrender.com/mcp-log/user_default
# Expected: {"deleted": <count>}

# Frontend
open https://<frontend>.vercel.app
```

### Frontend pages

| Page | Description |
|------|-------------|
| **Chat** | Chat with the AI agent. Each response shows a translation pipeline (your question → AI tool call → MCP JSON-RPC → AI reply). |
| **Wallet** | View simulated wallet balance. |
| **Transactions** | View trade history. |
| **MCP Inspector** | Two tabs: **Live** (current session MCP calls) and **History** (all past calls from MongoDB, paginated). |
| **How It Works** | Architecture diagrams and explanations. |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message to the AI agent. Returns `response`, `user_id`, and `steps` (agent reasoning + MCP JSON-RPC logs). |
| `GET` | `/balance/{user_id}` | Get wallet balance (no LLM call). |
| `GET` | `/transactions/{user_id}?limit=20` | Get recent transaction history (no LLM call). |
| `GET` | `/mcp-log/{user_id}?source=live` | Get current session MCP calls (in-memory). |
| `GET` | `/mcp-log/{user_id}?source=history&limit=50&skip=0` | Get all past MCP calls from MongoDB (paginated). |
| `DELETE` | `/mcp-log/{user_id}` | Clear all persisted MCP logs for a user. |
| `GET` | `/health` | Health check. |

### MongoDB Collections

| Collection | Contents |
|------------|----------|
| `wallets` | User wallet balances (keyed by `_id` = user_id). |
| `transactions` | Buy/sell transaction records with price, amount, timestamp. |
| `mcp_logs` | Every MCP JSON-RPC request/response pair, persisted for history. |

## Deploy Script (One-Command)

For convenience, a `deploy.sh` script is included in the repo root:

```bash
# Install CLIs (one-time)
brew install render
npm install -g vercel

# Deploy both
./deploy.sh

# Or individually
./deploy.sh backend
./deploy.sh frontend
```

The script handles authentication, environment variables, and deployment.
For Render, the first deployment requires a one-time Blueprint setup via the dashboard.

## Managing the Deployment

### Suspend / Resume (Save Resources)

```bash
# Suspend backend (stop)
curl -X POST "https://api.render.com/v1/services/<service-id>/suspend" \
  -H "Authorization: Bearer <render-api-key>"

# Resume backend (start)
curl -X POST "https://api.render.com/v1/services/<service-id>/resume" \
  -H "Authorization: Bearer <render-api-key>"

# Restart (if stuck after resume)
curl -X POST "https://api.render.com/v1/services/<service-id>/restart" \
  -H "Authorization: Bearer <render-api-key>"
```

The Vercel frontend does not need to be suspended -- it serves static files at zero cost.

### Auto-Deploy

Both platforms auto-deploy when you push to `main`:
- **Vercel**: Rebuilds the frontend automatically (takes ~30s)
- **Render**: Rebuilds and redeploys the backend automatically (takes ~3-5min)

### Updating Environment Variables

**Render** (backend): Change env vars in the Render dashboard or via API, then trigger a redeploy. A simple restart does NOT pick up env var changes -- a new deploy is required.

**Vercel** (frontend): Change env vars in the Vercel dashboard, then trigger a redeploy. Since `VITE_API_URL` is a build-time variable, changes require a rebuild.

## Troubleshooting

### "Failed to fetch" errors in the browser

**Cause**: CORS is blocking the request. The backend only allows specific origins.

**Fix**: Ensure `FRONTEND_URL` is set on Render to your Vercel URL. The backend also allows all `*.vercel.app` origins via regex, but `FRONTEND_URL` is needed as the primary allowed origin.

### "Service unavailable from a restricted location" from Binance

**Cause**: Render's servers are in the US. Binance blocks API requests from US IP addresses.

**Fix**: Set `DEFAULT_EXCHANGE=kraken` on Render (already configured in `render.yaml`). Kraken has no geo-restrictions. Your local `.env` can still use `binance` if you're outside the US.

### Backend returns 502 after resume

**Cause**: The service is still starting up after being suspended. Free-tier cold starts take 30-50 seconds.

**Fix**: Wait 1-2 minutes, then try again. If it persists, trigger a restart:
```bash
curl -X POST "https://api.render.com/v1/services/<service-id>/restart" \
  -H "Authorization: Bearer <render-api-key>"
```

### PYTHON_VERSION error on Render

**Cause**: Render requires a full version with patch number (e.g. `3.11.11`), not just `3.11`.

**Fix**: Already fixed in `render.yaml`. If you see this error, ensure `PYTHON_VERSION` is set to `3.11.11`.

### Render build takes too long or fails

**Cause**: Free-tier builds have limited resources.

**Fix**: Check the deploy logs in the Render dashboard or via CLI:
```bash
render logs --resources <service-id> --limit 30
```

## Current Live URLs

> **Not currently deployed.** Follow Steps 1–3 above to redeploy, then fill in the URLs below.

| Service | URL |
|---------|-----|
| Frontend | `https://<project-name>.vercel.app` |
| Backend | `https://<service-name>.onrender.com` |
| Health Check | `https://<service-name>.onrender.com/health` |
