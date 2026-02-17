import Mermaid from './Mermaid';
import {
  MessageSquare,
  Search,
  BookOpen,
  ShoppingCart,
  Wallet,
  ClipboardList,
  Globe,
} from 'lucide-react';
import './ArchitecturePage.scss';

const highLevelChart = `flowchart TD
  User["You (Browser)"]
  UI["React Frontend"]
  API["FastAPI Backend"]
  Agent["AI Agent (LangChain + Gemini)"]
  Tools["Agent Tools"]
  MCP["MCP Server (FastMCP + Bridge)"]
  CCXT["CCXT Client"]
  Exchange["Crypto Exchange (Kraken/Binance)"]
  DB["MongoDB Database"]

  User -->|"Type a message"| UI
  UI -->|"Send request"| API
  API -->|"Pass to agent"| Agent
  Agent -->|"Pick the right tool"| Tools
  Tools -->|"JSON-RPC request"| MCP
  MCP -->|"Need market data?"| CCXT
  CCXT -->|"Fetch live prices"| Exchange
  Exchange -->|"Price data"| CCXT
  CCXT -->|"Return data"| MCP
  MCP -->|"Need wallet data?"| DB
  DB -->|"Balance / history"| MCP
  MCP -->|"JSON-RPC response"| Tools
  Tools -->|"Tool result"| Agent
  Agent -->|"Natural language reply"| API
  API -->|"JSON response"| UI
  UI -->|"Show answer"| User`;

const chatFlowChart = `sequenceDiagram
  actor You
  participant UI as React UI
  participant API as FastAPI
  participant Agent as AI Agent
  participant LLM as Gemini LLM
  participant Tool as Price Tool
  participant CCXT as CCXT Client
  participant Exchange as Exchange

  You->>UI: "What is the price of BTC?"
  UI->>API: POST /chat
  API->>Agent: Process message
  Agent->>LLM: Understand intent
  LLM->>Tool: Call get_crypto_price
  Tool->>CCXT: get_ticker("BTC")
  CCXT->>Exchange: Fetch BTC/USDT price
  Exchange-->>CCXT: $68,887.90
  CCXT-->>Tool: Formatted price data
  Tool-->>LLM: "BTC is $68,887.90"
  LLM-->>Agent: Compose reply
  Agent-->>API: "Bitcoin is trading at $68,887"
  API-->>UI: JSON response
  UI-->>You: Display formatted answer`;

const buyFlowChart = `sequenceDiagram
  actor You
  participant UI as React UI
  participant API as FastAPI
  participant Agent as AI Agent
  participant BuyTool as Buy Tool
  participant CCXT as CCXT Client
  participant Exchange as Exchange
  participant DB as MongoDB

  You->>UI: "Buy $100 of ETH"
  UI->>API: POST /chat
  API->>Agent: Process message
  Agent->>BuyTool: buy_crypto("ETH", 100)
  BuyTool->>CCXT: Get current ETH price
  CCXT->>Exchange: Fetch ETH/USDT
  Exchange-->>CCXT: $1,972.25
  CCXT-->>BuyTool: price = $1,972.25
  Note over BuyTool: Calculate: $100 / $1972.25 = 0.05070 ETH
  BuyTool->>DB: Deduct $100 USD, add 0.05070 ETH
  DB-->>BuyTool: Wallet updated
  BuyTool->>DB: Record transaction
  DB-->>BuyTool: Transaction saved
  BuyTool-->>Agent: "Bought 0.05070 ETH at $1,972.25"
  Agent-->>API: Natural language confirmation
  API-->>UI: JSON response
  UI-->>You: Show confirmation
  Note over UI: Auto-refresh wallet and transactions`;

const deploymentChart = `flowchart LR
  subgraph user [User]
    Browser["Browser"]
  end

  subgraph vercel [Vercel - Free Tier]
    Frontend["React Static Build"]
  end

  subgraph render [Render - Free Tier]
    Backend["FastAPI + LangChain"]
  end

  subgraph external [External Services]
    Exchange["Kraken API"]
    MongoDB["MongoDB Atlas M0"]
    GenAI["HKBU GenAI API"]
  end

  Browser -->|"HTTPS"| Frontend
  Frontend -->|"VITE_API_URL"| Backend
  Backend -->|"CCXT"| Exchange
  Backend -->|"pymongo"| MongoDB
  Backend -->|"langchain-openai"| GenAI`;

const tools = [
  {
    icon: Search,
    name: 'Get Crypto Price',
    description:
      'Fetches the real-time price of any cryptocurrency from the exchange (Kraken in production, Binance locally). Ask "What is the price of BTC?" and this tool gets the live data.',
  },
  {
    icon: BookOpen,
    name: 'Get Order Book',
    description:
      'Shows the current buy and sell orders on the exchange. Useful for understanding market depth and liquidity.',
  },
  {
    icon: ShoppingCart,
    name: 'Buy Crypto',
    description:
      'Simulates buying cryptocurrency with your USD balance. It fetches the real price, calculates the amount, and updates your wallet.',
  },
  {
    icon: Wallet,
    name: 'Check Balance',
    description:
      'Returns your current wallet holdings with USD values. Shows how much of each crypto you own and what it is worth.',
  },
  {
    icon: ClipboardList,
    name: 'Transaction History',
    description:
      'Lists your recent trades including type (buy/sell), amount, price, and timestamp.',
  },
];

export default function ArchitecturePage() {
  return (
    <div className="arch">
      <div className="arch-header">
        <span className="arch-header__title">How It Works</span>
      </div>

      <div className="arch-content">
        {/* Section 1: Overview */}
        <section className="arch-section">
          <h2 className="arch-section__title">Overview</h2>
          <div className="arch-card">
            <p className="arch-text">
              This app lets you <strong>trade cryptocurrency using natural language</strong>.
              Instead of clicking buttons on an exchange, you just tell the AI what you want
              in plain English &mdash; like texting a friend who happens to be a trading expert.
            </p>
            <div className="arch-steps">
              <div className="arch-step">
                <div className="arch-step__number">1</div>
                <div className="arch-step__content">
                  <strong>You chat</strong> &mdash; Type a message like &ldquo;Buy $100 of Bitcoin&rdquo;
                  or &ldquo;What&rsquo;s the price of ETH?&rdquo;
                </div>
              </div>
              <div className="arch-step">
                <div className="arch-step__number">2</div>
                <div className="arch-step__content">
                  <strong>AI understands</strong> &mdash; The AI agent figures out what you want and
                  picks the right tool (check price, buy crypto, check balance, etc.)
                </div>
              </div>
              <div className="arch-step">
                <div className="arch-step__number">3</div>
                <div className="arch-step__content">
                  <strong>Real data, simulated trades</strong> &mdash; Prices come from a real exchange
                  (Kraken in production, Binance locally), but trades happen in a simulated wallet
                  (no real money). You start with $10,000.
                </div>
              </div>
              <div className="arch-step">
                <div className="arch-step__number">4</div>
                <div className="arch-step__content">
                  <strong>See results</strong> &mdash; The AI replies in plain English.
                  Your wallet and transaction history update automatically.
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: High-Level Architecture */}
        <section className="arch-section">
          <h2 className="arch-section__title">System Architecture</h2>
          <p className="arch-text arch-text--muted">
            The flowchart below shows how data flows through the entire system.
            Follow the arrows from top to bottom &mdash; your message travels through
            each layer, and the response comes back the same way.
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={highLevelChart} />
          </div>
          <div className="arch-card">
            <p className="arch-text" style={{ marginBottom: 12 }}>
              <strong>Reading the flowchart:</strong> Each box is a component of the system.
              Arrows show the direction of data flow, and labels describe what data is being passed.
              The left side handles <em>market data</em> (prices from the exchange), while the right
              side handles <em>user data</em> (wallet and transactions from MongoDB).
            </p>
            <div className="arch-legend">
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--blue" />
                <span><strong>Frontend</strong> &mdash; React app running in your browser (hosted on Vercel). Handles the chat UI, wallet display, and transaction history. Communicates with the backend via REST API calls.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--green" />
                <span><strong>Backend + AI Agent</strong> &mdash; Python FastAPI server (hosted on Render) with a LangChain agent powered by Gemini 2.5 Flash. The agent interprets your natural language and decides which tool to call.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--orange" />
                <span><strong>MCP Server (FastMCP + Bridge)</strong> &mdash; A real FastMCP server with an in-process bridge that speaks the MCP JSON-RPC protocol. Tools are defined once via <code>@mcp.tool()</code> decorators, return structured responses, and every call is logged as a JSON-RPC request/response pair visible in the MCP Inspector page. External MCP clients can also connect via SSE.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--orange" />
                <span><strong>CCXT Client</strong> &mdash; Library that connects to the exchange. The exchange is configurable &mdash; Kraken in production (US-friendly), Binance locally (Asia). No API key needed for public price data.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--purple" />
                <span><strong>MongoDB Atlas</strong> &mdash; Cloud database (free M0 tier) that persists your simulated wallet balance and transaction history across sessions.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Chat Flow */}
        <section className="arch-section">
          <h2 className="arch-section__title">What Happens When You Chat</h2>
          <p className="arch-text arch-text--muted">
            The sequence diagram below reads top-to-bottom like a timeline. Each vertical
            line is a component, and horizontal arrows show messages between them. Solid arrows
            are requests; dashed arrows are responses. Follow along to see exactly what happens
            when you ask &ldquo;What is the price of BTC?&rdquo;
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={chatFlowChart} />
          </div>
          <div className="arch-card">
            <p className="arch-text" style={{ marginBottom: 12 }}>
              <strong>Key takeaway:</strong> The AI agent acts as a smart router. It reads your
              message, understands the intent, picks the right tool, and translates the raw data
              into a human-friendly response. You never need to know which API to call &mdash;
              the agent handles it.
            </p>
            <ol className="arch-ol">
              <li>You type your question in the chat box and hit send.</li>
              <li>The React frontend sends a <em>POST /chat</em> request to the FastAPI backend.</li>
              <li>The AI agent (LangChain) passes your message to the Gemini LLM to understand intent.</li>
              <li>The LLM determines it needs price data and calls the <em>get_crypto_price</em> tool.</li>
              <li>The tool uses the CCXT library to query the exchange&rsquo;s public API for BTC/USDT.</li>
              <li>The exchange returns real-time market data (price, bid, ask, volume, 24h high/low).</li>
              <li>The LLM formats a natural-language reply and sends it back through the chain.</li>
              <li>The frontend displays the answer in the chat &mdash; the whole round trip takes 3-8 seconds.</li>
            </ol>
          </div>
        </section>

        {/* Section 4: Buy Flow */}
        <section className="arch-section">
          <h2 className="arch-section__title">What Happens When You Buy Crypto</h2>
          <p className="arch-text arch-text--muted">
            This sequence diagram shows a more complex flow with <strong>two external
            services</strong> (exchange + database). Notice how the Buy Tool acts as an
            orchestrator &mdash; it coordinates between the exchange for pricing and MongoDB
            for wallet updates, all within a single tool call.
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={buyFlowChart} />
          </div>
          <div className="arch-card">
            <p className="arch-text" style={{ marginBottom: 12 }}>
              <strong>Key takeaway:</strong> The buy operation is <em>atomic</em> &mdash; the tool
              checks your balance, fetches the price, updates the wallet, and records the transaction
              all in one step. If any step fails (e.g. insufficient funds), the whole operation is
              rolled back and the agent reports the error.
            </p>
            <ol className="arch-ol">
              <li>The AI recognizes you want to buy and calls the <em>buy_crypto</em> tool with symbol and USD amount.</li>
              <li>The tool fetches the current ETH price from the exchange (e.g. $1,972.25).</li>
              <li>It calculates how much ETH $100 buys: 100 &divide; 1972.25 = 0.05070 ETH.</li>
              <li>Your MongoDB wallet is updated: $100 deducted from USD, 0.05070 ETH added.</li>
              <li>A transaction record is saved with price, amount, USD value, and timestamp.</li>
              <li>The AI confirms the trade in plain English with a breakdown of the purchase.</li>
              <li>Your Wallet and Transactions pages refresh automatically via Redux state updates.</li>
            </ol>
          </div>
        </section>

        {/* Section 5: AI Agent Toolbox */}
        <section className="arch-section">
          <h2 className="arch-section__title">The AI Agent&rsquo;s Toolbox</h2>
          <p className="arch-text arch-text--muted">
            The AI agent has 5 tools it can use. Based on what you say, it automatically picks
            the right one (or multiple). Think of them like apps on a phone &mdash; the AI opens
            the right app for the job.
          </p>
          <div className="arch-tools">
            {tools.map((tool) => (
              <div key={tool.name} className="arch-tool">
                <div className="arch-tool__icon">
                  <tool.icon size={20} />
                </div>
                <div className="arch-tool__body">
                  <div className="arch-tool__name">{tool.name}</div>
                  <div className="arch-tool__desc">{tool.description}</div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Section 6: Deployment Architecture */}
        <section className="arch-section">
          <h2 className="arch-section__title">Deployment Architecture</h2>
          <p className="arch-text arch-text--muted">
            This flowchart shows how the app is deployed in production. The entire stack runs
            on <strong>free-tier services</strong> ($0/month). The frontend is a static build
            on Vercel, and the backend runs as a web service on Render.
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={deploymentChart} />
          </div>
          <div className="arch-card">
            <p className="arch-text" style={{ marginBottom: 12 }}>
              <strong>Why Kraken instead of Binance?</strong> The backend runs on Render&rsquo;s
              servers in Oregon, USA. Binance blocks API requests from US IP addresses, so
              the production deployment uses Kraken (which has no geo-restrictions). Locally,
              you can still use Binance if you&rsquo;re outside the US. The exchange is
              configurable via the <em>DEFAULT_EXCHANGE</em> environment variable.
            </p>
            <div className="arch-legend">
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--blue" />
                <span><strong>Vercel (Free)</strong> &mdash; Hosts the React static build. Auto-deploys on git push. Global CDN for fast loading.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--green" />
                <span><strong>Render (Free)</strong> &mdash; Runs the FastAPI backend. Sleeps after 15min of inactivity; first request after sleep takes ~30-50s.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--orange" />
                <span><strong>Kraken API</strong> &mdash; Public market data with no geo-restrictions. No API key required for price queries.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--purple" />
                <span><strong>MongoDB Atlas M0</strong> &mdash; Free cloud database (512MB). Stores wallet balances and transaction history.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 7: Tech Stack */}
        <section className="arch-section">
          <h2 className="arch-section__title">Tech Stack</h2>
          <div className="arch-card">
            <div className="arch-stack">
              <div className="arch-stack__row">
                <span className="arch-stack__label">Frontend</span>
                <span className="arch-stack__value">React, TypeScript, Redux Toolkit, Vite</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">Backend</span>
                <span className="arch-stack__value">Python, FastAPI, LangChain, FastMCP</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">AI Model</span>
                <span className="arch-stack__value">Gemini 2.5 Flash (via HKBU GenAI API)</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">Market Data</span>
                <span className="arch-stack__value">CCXT &rarr; Kraken (prod) / Binance (local)</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">Database</span>
                <span className="arch-stack__value">MongoDB Atlas (cloud, free M0 tier)</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">Hosting</span>
                <span className="arch-stack__value">Vercel (frontend) + Render (backend) &mdash; $0/month</span>
              </div>
            </div>
          </div>
        </section>

        <footer className="arch-footer">
          <MessageSquare size={14} />
          <span>Go to the <strong>Chat</strong> tab to start trading with AI</span>
        </footer>
      </div>
    </div>
  );
}
