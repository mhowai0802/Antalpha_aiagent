# Crypto Trading AI Agent — Complete Project Overview

This document is a comprehensive source for understanding the Crypto Trading AI Agent project. It covers what the app does, how it works, the full system architecture, the MCP protocol layer, how the AI translates natural language into structured tool calls, deployment infrastructure, and how it compares to traditional cryptocurrency trading.

---

## 1. What Is This App?

This application lets users trade cryptocurrency using natural language. Instead of logging into an exchange like Binance or Coinbase, navigating complex menus, clicking Buy, and entering amounts, users simply type what they want in plain English — like texting a friend who happens to be a trading expert.

For example, a user can type "What's the price of Bitcoin?" or "Buy $100 of Ethereum" and the AI agent understands, executes the request, and replies in plain English.

Important: all trades are simulated. Users start with $10,000 in play money. The prices are real (fetched live from a real exchange), but no real money is ever spent. This makes the app ideal for learning, testing strategies, or experiencing crypto trading without financial risk.

### How It Works in 4 Steps

1. You chat: Type a message like "Buy $100 of Bitcoin" or "What's the price of ETH?" in the chat interface.
2. AI understands: The AI agent (powered by Google's Gemini 2.5 Flash model) figures out what you want and picks the right tool — check a price, execute a buy, check your balance, etc.
3. Real data, simulated trades: Prices come from a real cryptocurrency exchange (Kraken in production, Binance for local development). Trades happen in a simulated wallet stored in MongoDB — no real money involved. Every user starts with $10,000 USD.
4. See results: The AI replies in plain English with the information or confirmation. Your wallet balance and transaction history update automatically in the UI.

---

## 2. System Architecture

The application has five layers, from the user's browser all the way down to external services.

### Layer 1: Frontend (React on Vercel)

The frontend is a React single-page application built with TypeScript, Vite, and Redux Toolkit. It runs in the user's browser and is hosted as a static build on Vercel (free tier). It has five pages:

- Chat: The main page where users talk to the AI agent. Each AI response includes a "translation pipeline" showing how the user's natural language was converted into a structured tool call, passed through the MCP server as JSON-RPC, and then translated back into a natural language reply.
- Wallet: Displays the user's simulated wallet balance with USD values for each cryptocurrency held.
- Transactions: Shows the history of all simulated trades with type, amount, price, and timestamp.
- MCP Inspector: A dedicated page for viewing MCP (Model Context Protocol) JSON-RPC logs. Has two tabs — "Live" for the current session and "History" for all past calls persisted in MongoDB.
- How It Works: Interactive architecture diagrams built with Mermaid, explaining the system visually.

The frontend communicates with the backend exclusively through REST API calls (fetch to FastAPI endpoints).

### Layer 2: Backend (FastAPI on Render)

The backend is a Python FastAPI server hosted on Render (free tier). It exposes the following API endpoints:

- POST /chat: The main endpoint. Receives a user message, passes it to the AI agent, and returns the agent's response along with intermediate reasoning steps and MCP logs.
- GET /balance/{user_id}: Returns the user's wallet balance directly from MongoDB (no AI involved).
- GET /transactions/{user_id}: Returns recent transaction history from MongoDB.
- GET /mcp-log/{user_id}?source=live or source=history: Returns MCP call logs. "live" returns current session logs from memory. "history" returns all past logs from MongoDB with pagination (limit and skip parameters).
- DELETE /mcp-log/{user_id}: Clears all persisted MCP logs for a user.
- GET /health: Simple health check endpoint.

### Layer 3: AI Agent (LangChain + Gemini)

The AI agent is built with LangChain and uses Google's Gemini 2.5 Flash model (accessed through the HKBU GenAI API in Azure OpenAI format). When a user message arrives:

1. The message is passed to the LangChain AgentExecutor.
2. The Gemini LLM reads the message and decides which tool (or tools) to call.
3. It generates a structured tool call with specific arguments (e.g., tool: "get_crypto_price", arguments: {"symbol": "BTC"}).
4. The tool executes and returns raw data.
5. The LLM reads the tool result and composes a natural language reply.
6. The reply and all intermediate steps (tool calls, MCP logs) are returned to the frontend.

The agent has access to 5 tools:

- get_crypto_price: Fetches real-time price for any cryptocurrency (BTC, ETH, SOL, etc.) from the exchange. Returns current price, bid, ask, 24-hour high/low, and volume.
- get_orderbook: Gets the order book (buy/sell depth) for a trading pair, showing current market bids and asks.
- buy_crypto: Simulates buying cryptocurrency with USD. Fetches real price, calculates how much crypto the USD amount buys, deducts USD from the wallet, adds the crypto, and records a transaction.
- check_balance: Returns the user's wallet holdings with current USD values for each asset.
- transaction_history: Lists recent trades with type (buy/sell), amount, price, USD value, and timestamp.

### Layer 4: MCP Protocol Layer (FastMCP Server + Bridge)

This is a key educational feature of the application. Between the AI agent's tools and the actual external services (exchange API and database), there is a real MCP (Model Context Protocol) server built with the official FastMCP SDK, connected to the LangChain agent through an in-process bridge that handles JSON-RPC logging.

#### What is MCP?

MCP (Model Context Protocol) is a standard protocol created by Anthropic for AI models to interact with external tools and data sources. It uses JSON-RPC 2.0 as its message format. In a production MCP setup, an MCP server runs as a separate process and communicates over stdio, SSE, or HTTP.

#### Architecture: FastMCP + Bridge

The MCP layer follows the same architecture as the official Binance MCP server:

- **FastMCP Server (server.py)**: Tools are defined once using `@mcp.tool()` decorators — the single source of truth for tool names, descriptions, and parameter schemas. The server is also mounted on the FastAPI app via SSE at `/mcp`, so external MCP clients (like Claude Desktop or Cursor) can connect to it.
- **Handlers (handlers.py)**: Standalone handler functions that contain the actual business logic. Each handler returns a structured Dict response following the Binance MCP pattern: `{"success": true, "data": {...}, "timestamp": ...}` for success, or `{"success": false, "error": {"type": "...", "message": "..."}}` for errors.
- **Shared Utilities (utils.py)**: Standardized response builders (`create_success_response`, `create_error_response`), input validators (`validate_symbol`, `validate_positive_number`), and a rate limiter (`@rate_limited` decorator with a sliding-window `RateLimiter` class).
- **MCP Bridge (bridge.py)**: An in-process bridge that connects LangChain tools to the handlers. It calls handlers directly (no transport overhead) while constructing JSON-RPC 2.0 request/response log entries for the MCP Inspector UI and persisting them to MongoDB.

#### How the MCP Bridge Works

When a LangChain tool is invoked (e.g., get_crypto_price), instead of calling the exchange API directly, it sends a request through the MCP bridge. Here is what happens:

Step 1 — The tool calls mcp_bridge.call_tool("get_crypto_price", {"symbol": "BTC"}).

Step 2 — The bridge constructs a JSON-RPC 2.0 request:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_crypto_price",
    "arguments": {"symbol": "BTC"}
  },
  "id": 1
}
```

Step 3 — The bridge calls the registered handler for "get_crypto_price". The handler validates the input using `validate_symbol()`, then uses the CCXT library to fetch the price from the exchange, and returns a structured response:
```json
{
  "success": true,
  "data": {
    "symbol": "BTC/USDT",
    "last": 68887.90,
    "bid": 68885.00,
    "ask": 68890.00,
    "high": 69241.50,
    "low": 66734.30,
    "volume": 18432.56
  },
  "timestamp": 1771345659427,
  "metadata": {"source": "ccxt", "endpoint": "get_ticker"}
}
```

Step 4 — The bridge converts the structured result to display text and wraps it in a JSON-RPC 2.0 response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"symbol\": \"BTC/USDT\", \"last\": 68887.90, ...}"
      }
    ],
    "isError": false,
    "_structured": {"success": true, "data": {...}, "timestamp": ...}
  },
  "id": 1
}
```

Step 5 — Both the request and response are logged in memory (for the "Live" tab) and persisted to MongoDB's mcp_logs collection (for the "History" tab). The `_structured` field preserves the raw typed data for inspection.

Step 6 — The text content from the response is returned to the LangChain tool, which passes it back to the LLM.

This means every single tool call is visible to the user in two places: the translation pipeline in the Chat page (showing the full chain from natural language to JSON-RPC and back) and the MCP Inspector page (showing all JSON-RPC request/response pairs).

#### Why This Matters

The MCP layer makes the AI's decision-making completely transparent. Users can see:
- What the AI decided to do (which tool, what arguments)
- The exact standardized format the request was sent in (JSON-RPC)
- The raw data that came back from the exchange or database
- How the AI translated that raw data into a human-friendly response

This is valuable for education (understanding how AI agents work), debugging (seeing exactly what went wrong), and trust (no hidden black-box behavior).

### Layer 5: External Services

- Crypto Exchange (Kraken/Binance): The CCXT library connects to a real cryptocurrency exchange to fetch live market data. In production (deployed on Render's US servers), Kraken is used because Binance blocks US IP addresses. Locally, developers can use Binance. The exchange is configurable via the DEFAULT_EXCHANGE environment variable. No API key is needed — only public price data is accessed.
- MongoDB Atlas: A cloud-hosted MongoDB database on the free M0 tier (512 MB). Stores three collections: wallets (user balances), transactions (trade records), and mcp_logs (every MCP JSON-RPC call for the History feature).
- HKBU GenAI API: The university-provided API that gives access to Google's Gemini 2.5 Flash model in Azure OpenAI format. This is the LLM that powers the AI agent's understanding and responses.

---

## 3. How the AI Translates Your Question

This is the core innovation visible in the UI. When a user asks "how much is btc?", here is the complete chain:

### The Translation Pipeline (visible in the Chat page)

Row 1 — AI understands your question:
- Left side: Your natural language input — "how much is btc?"
- Right side: The AI's structured decision — Tool: get_crypto_price, Arguments: {"symbol": "BTC"}

Row 2 — MCP Server processes (JSON-RPC):
- Left side: The JSON-RPC request sent to the MCP server
- Right side: The JSON-RPC response received back, containing the raw price data

Row 3 — AI composes reply:
- Left side: The raw tool output (structured price data with current, bid, ask, high, low, volume)
- Right side: The AI's natural language reply — "Bitcoin is currently trading at $68,887.90..."

This pipeline is shown directly under every AI response in the chat, so users always see how their natural language was transformed into a structured API call and back.

---

## 4. Detailed Flow: Asking a Price Question

When a user asks "What is the price of BTC?", this is the exact sequence of events:

1. The user types the question in the chat input and presses send.
2. The React frontend dispatches a Redux thunk that sends a POST request to /chat with the message.
3. The FastAPI backend receives the request and passes the message to the LangChain AgentExecutor.
4. The AgentExecutor sends the message to the Gemini LLM with the system prompt and available tool definitions.
5. The LLM analyzes the user's intent and determines it needs to call get_crypto_price with argument symbol="BTC".
6. The LangChain tool's _run method is called. Instead of querying the exchange directly, it calls mcp_bridge.call_tool("get_crypto_price", {"symbol": "BTC"}).
7. The MCP bridge constructs a JSON-RPC request, calls the registered handler (which validates the input, then uses CCXT to query the exchange's public API for BTC/USDT).
8. The handler returns a structured Dict with the market data: current price, bid, ask, 24-hour high, 24-hour low, and volume.
9. The MCP bridge wraps the structured result in a JSON-RPC response, logs both request and response (in memory and to MongoDB), and returns the text content.
10. The tool result flows back to the LLM, which composes a friendly natural-language reply.
11. The AgentExecutor returns the final output along with intermediate_steps (containing the tool call details and MCP logs).
12. The FastAPI endpoint packages everything into a response with response (the text), steps (the agent reasoning with MCP request/response pairs), and user_id.
13. The frontend receives the response, displays the AI's reply in a chat bubble, and shows the translation pipeline directly below it.
14. The frontend also automatically refreshes the Wallet and Transactions pages via Redux dispatches.

The entire round trip takes approximately 3 to 8 seconds.

---

## 5. Detailed Flow: Buying Cryptocurrency

When a user says "Buy $100 of ETH", a more complex flow occurs because it involves two external services (exchange for pricing, database for wallet updates):

1. The AI recognizes the buy intent and calls buy_crypto with arguments symbol="ETH" and amount=100.
2. The tool sends a JSON-RPC request to the MCP bridge for "buy_crypto".
3. The handler validates the input (symbol and amount), then fetches the current ETH price from the exchange via CCXT (e.g., $1,972.25).
4. It calculates how much ETH $100 buys: 100 / 1972.25 = 0.05070 ETH.
5. It checks the user's wallet in MongoDB to ensure they have at least $100 USD.
6. It performs an atomic MongoDB update: deducts $100 from USD balance and adds 0.05070 to ETH balance.
7. It inserts a transaction record into the transactions collection with the trade details.
8. The handler returns a structured success response. The MCP bridge logs the JSON-RPC pair and returns the text to the LLM.
9. The AI composes a confirmation message: "Bought 0.05070 ETH at $1,972.25, spent $100.00 USD."
10. The frontend displays the confirmation and auto-refreshes the Wallet and Transactions pages.

The buy operation is atomic — if any step fails (for example, insufficient funds), the entire operation is rolled back and the AI reports the error to the user.

---

## 6. Normal Bitcoin Buying vs This App

This comparison helps non-technical users understand what makes this app different from traditional cryptocurrency exchanges:

How you interact:
- Normal: Log into an exchange (Binance, Coinbase), navigate complex menus, click Buy, manually enter amount and price, confirm the order.
- This app: Type in plain English — "Buy $100 of Bitcoin." Done.

Understanding needed:
- Normal: You must understand order types, trading pairs, fee structures, and exchange interfaces.
- This app: AI understands natural language. No training or prior knowledge needed.

Price lookup:
- Normal: You manually check the price chart on the exchange before deciding to buy.
- This app: AI fetches the real-time price automatically and shows it to you.

Execution:
- Normal: You confirm the order and real money is spent from your exchange account.
- This app: AI simulates the trade using a demo wallet with $10,000 play money. No real money involved.

Wallet and history:
- Normal: Stored on the exchange's servers. You need to log in to view them.
- This app: Stored in MongoDB. Visible directly in the app's Wallet and Transactions pages.

Best for:
- Normal: Actual investing with real funds.
- This app: Learning how crypto trading works, testing strategies, or trying crypto without any financial risk.

In short: Normal buying means you do everything manually on an exchange. This app means you chat, the AI does the work, and everything is simulated so you can learn safely.

---

## 7. The MCP Inspector Page

The MCP Inspector is a dedicated page in the application that provides full visibility into every JSON-RPC call made through the MCP protocol layer. It has two tabs:

Live tab: Shows MCP calls from the current browser session only. This is fetched from the in-memory log on the backend. It updates every time you refresh. Useful for seeing what just happened during your current conversation.

History tab: Shows all MCP calls ever made, persisted in MongoDB's mcp_logs collection. This data survives server restarts and is paginated (50 entries per page with a "Load more" button). Useful for reviewing past conversations and seeing cumulative usage patterns.

Each MCP call is displayed as a card with two panels side by side:
- Left panel: The JSON-RPC request (showing method, tool name, and arguments)
- Right panel: The JSON-RPC response (showing the result content and whether it was an error)

The header of each card shows the tool name and timestamp.

Users can clear history by clicking "Clear History" in the History tab, which sends a DELETE request to /mcp-log/{user_id}.

---

## 8. Tech Stack

Frontend: React 18 with TypeScript, Redux Toolkit for state management, Vite for building, SCSS for styling, react-markdown for rendering AI responses, lucide-react for icons, and mermaid for architecture diagrams.

Backend: Python 3.11, FastAPI for the web server, LangChain for the AI agent framework, FastMCP for the MCP server (with @mcp.tool() decorators and SSE transport), Pydantic for data validation, uvicorn as the ASGI server.

AI Model: Google Gemini 2.5 Flash, accessed through the HKBU GenAI API (which provides an Azure OpenAI-compatible endpoint).

Market Data: CCXT library connecting to Kraken (production) or Binance (local development) for real-time cryptocurrency prices. No API key required for public endpoints.

Database: MongoDB Atlas on the free M0 tier (512 MB storage). Three collections: wallets, transactions, and mcp_logs.

Hosting: Vercel (frontend, free tier, auto-deploys on git push, global CDN) and Render (backend, free tier, sleeps after 15 minutes of inactivity, cold start takes 30-50 seconds).

Total monthly cost: $0.

---

## 9. Deployment Architecture

The entire application runs on free-tier cloud services:

Browser connects via HTTPS to Vercel, which serves the React static build. Vercel connects to the Render backend using the VITE_API_URL environment variable set at build time.

The Render backend (FastAPI + LangChain + FastMCP Bridge) connects to three external services:
- Kraken API via the CCXT library for live cryptocurrency prices
- MongoDB Atlas M0 via pymongo for wallet, transaction, and MCP log persistence
- HKBU GenAI API via langchain-openai for the Gemini 2.5 Flash LLM

Why Kraken instead of Binance in production? The backend runs on Render's servers in Oregon, USA. Binance blocks API requests from US IP addresses. Kraken has no geo-restrictions and works globally. The exchange is configurable via the DEFAULT_EXCHANGE environment variable, so local developers outside the US can still use Binance.

Vercel auto-deploys the frontend whenever code is pushed to the main branch (takes about 30 seconds). Render auto-deploys the backend on push as well (takes 3-5 minutes). Both can also be deployed manually using the deploy.sh script or CLI tools.

---

## 10. MongoDB Data Model

The application uses three MongoDB collections:

### wallets collection
Each document represents a user's wallet. The _id field is the user_id (e.g., "user_default"). The assets field is a dictionary mapping asset names to balances (e.g., {"USD": 9900.00, "BTC": 0.00145, "ETH": 0.05070}). New users are initialized with $10,000 USD.

### transactions collection
Each document records a single trade with fields: user_id, type (BUY), symbol (e.g., BTC), amount (crypto amount), price (price at time of trade), usd_value (USD spent), and timestamp.

### mcp_logs collection
Each document records one MCP JSON-RPC call with fields: user_id, type ("tools/call" or "tools/list"), request (the full JSON-RPC request object), response (the full JSON-RPC response object), timestamp (Unix epoch), and created_at (ISO string).

---

## 11. Project Structure

```
Antalpha_aiagent/
├── backend/
│   ├── main.py                    # FastAPI server with all endpoints + FastMCP SSE mount
│   ├── agent/
│   │   ├── crypto_agent.py        # LangChain agent setup (AgentWithMCP wrapper)
│   │   └── tools.py               # Auto-generated LangChain tools from spec table
│   ├── mcp_server/
│   │   ├── server.py              # FastMCP server — @mcp.tool() definitions (single source of truth)
│   │   ├── bridge.py              # MCPBridge — JSON-RPC logging wrapper for LangChain integration
│   │   ├── handlers.py            # Handler functions returning structured Dict responses
│   │   ├── utils.py               # Shared utilities: validators, response builders, rate limiter
│   │   └── registry.py            # Factory that creates MCPBridge for a user
│   ├── mcp_client/
│   │   └── ccxt_client.py         # CCXT wrapper for exchange API calls
│   ├── db/
│   │   └── mongo.py               # MongoDB operations (wallets, transactions, mcp_logs)
│   └── requirements.txt           # Includes fastmcp>=2.0.0
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Root component with page routing
│   │   ├── api/agentApi.ts        # API client functions
│   │   ├── store/
│   │   │   ├── chatSlice.ts       # Chat state (messages with steps)
│   │   │   ├── mcpSlice.ts        # MCP log state (live + history)
│   │   │   ├── walletSlice.ts     # Wallet balance state
│   │   │   └── transactionsSlice.ts
│   │   └── components/
│   │       ├── ChatPage.tsx        # Chat UI with translation pipeline
│   │       ├── MCPInspectorPage.tsx # MCP log viewer (Live/History tabs)
│   │       ├── WalletPage.tsx
│   │       ├── TransactionsPage.tsx
│   │       ├── ArchitecturePage.tsx # Interactive architecture diagrams
│   │       └── Sidebar.tsx
│   └── package.json
├── deploy.sh                       # One-command deployment script
├── render.yaml                     # Render Blueprint configuration
├── DEPLOYMENT.md                   # Detailed deployment guide
├── Architecture_Explained.md       # Architecture documentation
└── README.md                       # Project readme with setup instructions
```

---

## 12. Key Design Decisions

### Why simulate trades instead of executing real ones?
The app is designed for education and demonstration. Real trading requires KYC verification, API keys with trading permissions, and carries financial risk. Simulated trading lets users experience the full flow safely.

### Why use FastMCP with a bridge instead of a standalone MCP server?
The project uses the official FastMCP SDK to define tools via `@mcp.tool()` decorators — following the same pattern as the Binance MCP server. This gives us a real MCP server (mountable via SSE for external clients like Claude Desktop or Cursor) while keeping the LangChain agent integration in-process through the MCPBridge. The bridge provides JSON-RPC logging for the Inspector UI without transport overhead. Handlers return structured Dict responses with the `{success, data, error}` pattern, input validation via shared utilities, and rate limiting — all modeled after production MCP server best practices.

### Why LangChain instead of calling the LLM directly?
LangChain provides the AgentExecutor framework that handles the tool-calling loop automatically — the LLM decides which tool to call, LangChain executes it, passes the result back, and lets the LLM decide if it needs to call another tool or compose a final response. This multi-step reasoning would be complex to build from scratch.

### Why Gemini 2.5 Flash?
It is available through the HKBU university API at no cost, supports tool calling (function calling), has fast response times, and produces high-quality natural language output.

### Why Kraken over Binance in production?
Render's servers are in the US, and Binance blocks US IP addresses. Kraken has no geo-restrictions. Both exchanges are supported through the CCXT library — switching is a single environment variable change.

---

## 13. Live Demo URLs

- Frontend: https://crypto-agent-frontend-blond.vercel.app
- Backend: https://crypto-agent-backend-oyyf.onrender.com
- Health Check: https://crypto-agent-backend-oyyf.onrender.com/health

Note: The backend runs on Render's free tier and sleeps after 15 minutes of inactivity. The first request after sleeping takes 30-50 seconds to wake up. Subsequent requests are fast.
