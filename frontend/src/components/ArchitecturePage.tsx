import Mermaid from './Mermaid';
import {
  MessageSquare,
  Search,
  BookOpen,
  ShoppingCart,
  Wallet,
  ClipboardList,
} from 'lucide-react';
import './ArchitecturePage.scss';

const highLevelChart = `flowchart TD
  User["You (Browser)"]
  UI["React Frontend"]
  API["FastAPI Backend"]
  Agent["AI Agent (LangChain + Gemini)"]
  Tools["Agent Tools"]
  CCXT["MCP Client (CCXT)"]
  Binance["Binance Exchange"]
  DB["MongoDB Database"]

  User -->|"Type a message"| UI
  UI -->|"Send request"| API
  API -->|"Pass to agent"| Agent
  Agent -->|"Pick the right tool"| Tools
  Tools -->|"Need market data?"| CCXT
  CCXT -->|"Fetch live prices"| Binance
  Binance -->|"Price data"| CCXT
  CCXT -->|"Return data"| Tools
  Tools -->|"Need wallet data?"| DB
  DB -->|"Balance / history"| Tools
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
  participant Binance as Binance

  You->>UI: "What is the price of BTC?"
  UI->>API: POST /chat
  API->>Agent: Process message
  Agent->>LLM: Understand intent
  LLM->>Tool: Call get_crypto_price
  Tool->>CCXT: get_ticker("BTC")
  CCXT->>Binance: Fetch BTC/USDT price
  Binance-->>CCXT: $45,123.45
  CCXT-->>Tool: Formatted price data
  Tool-->>LLM: "BTC is $45,123.45"
  LLM-->>Agent: Compose reply
  Agent-->>API: "Bitcoin is trading at $45,123"
  API-->>UI: JSON response
  UI-->>You: Display formatted answer`;

const buyFlowChart = `sequenceDiagram
  actor You
  participant UI as React UI
  participant API as FastAPI
  participant Agent as AI Agent
  participant BuyTool as Buy Tool
  participant CCXT as CCXT Client
  participant Binance as Binance
  participant DB as MongoDB

  You->>UI: "Buy $100 of ETH"
  UI->>API: POST /chat
  API->>Agent: Process message
  Agent->>BuyTool: buy_crypto("ETH", 100)
  BuyTool->>CCXT: Get current ETH price
  CCXT->>Binance: Fetch ETH/USDT
  Binance-->>CCXT: $3,200.50
  CCXT-->>BuyTool: price = $3,200.50
  Note over BuyTool: Calculate: $100 / $3200.50 = 0.03125 ETH
  BuyTool->>DB: Deduct $100 USD, add 0.03125 ETH
  DB-->>BuyTool: Wallet updated
  BuyTool->>DB: Record transaction
  DB-->>BuyTool: Transaction saved
  BuyTool-->>Agent: "Bought 0.03125 ETH at $3,200.50"
  Agent-->>API: Natural language confirmation
  API-->>UI: JSON response
  UI-->>You: Show confirmation
  Note over UI: Auto-refresh wallet and transactions`;

const tools = [
  {
    icon: Search,
    name: 'Get Crypto Price',
    description:
      'Fetches the real-time price of any cryptocurrency from Binance. Ask "What is the price of BTC?" and this tool gets the live data.',
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
                  <strong>Real data, simulated trades</strong> &mdash; Prices come from Binance (real!),
                  but trades happen in a simulated wallet (no real money). You start with $10,000.
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
            The app has three main layers: the <strong>frontend</strong> (what you see),
            the <strong>backend</strong> (the AI brain), and <strong>external services</strong> (Binance
            for prices, MongoDB for your wallet).
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={highLevelChart} />
          </div>
          <div className="arch-card">
            <div className="arch-legend">
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--blue" />
                <span><strong>Frontend</strong> &mdash; React app running in your browser. Handles the chat UI, wallet display, and transaction history.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--green" />
                <span><strong>Backend</strong> &mdash; Python server with an AI agent powered by LangChain and Gemini 2.5 Flash. Decides what to do with your message.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--orange" />
                <span><strong>MCP Client (CCXT)</strong> &mdash; A wrapper around the CCXT library that connects to Binance to fetch real-time cryptocurrency prices.</span>
              </div>
              <div className="arch-legend__item">
                <span className="arch-legend__dot arch-legend__dot--purple" />
                <span><strong>MongoDB</strong> &mdash; Cloud database that stores your simulated wallet balance and transaction history.</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Chat Flow */}
        <section className="arch-section">
          <h2 className="arch-section__title">What Happens When You Chat</h2>
          <p className="arch-text arch-text--muted">
            When you ask &ldquo;What is the price of BTC?&rdquo;, here is exactly what happens
            behind the scenes, step by step:
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={chatFlowChart} />
          </div>
          <div className="arch-card">
            <ol className="arch-ol">
              <li>You type your question in the chat box and hit send.</li>
              <li>The frontend sends your message to the backend API.</li>
              <li>The AI agent reads your message and decides it needs to look up a price.</li>
              <li>It calls the <em>get_crypto_price</em> tool, which uses CCXT to query Binance.</li>
              <li>Binance returns the real, live price of BTC.</li>
              <li>The AI formats a friendly reply and sends it back to you.</li>
            </ol>
          </div>
        </section>

        {/* Section 4: Buy Flow */}
        <section className="arch-section">
          <h2 className="arch-section__title">What Happens When You Buy Crypto</h2>
          <p className="arch-text arch-text--muted">
            When you say &ldquo;Buy $100 of ETH&rdquo;, the agent does more work &mdash;
            it fetches the price, calculates the amount, updates your wallet, and records the trade:
          </p>
          <div className="arch-card arch-card--diagram">
            <Mermaid chart={buyFlowChart} />
          </div>
          <div className="arch-card">
            <ol className="arch-ol">
              <li>The AI recognizes you want to buy and calls the <em>buy_crypto</em> tool.</li>
              <li>The tool fetches the current ETH price from Binance (e.g. $3,200.50).</li>
              <li>It calculates how much ETH $100 buys: 100 &divide; 3200.50 = 0.03125 ETH.</li>
              <li>Your MongoDB wallet is updated: $100 deducted from USD, 0.03125 ETH added.</li>
              <li>A transaction record is saved with price, amount, and timestamp.</li>
              <li>The AI confirms the trade in plain English.</li>
              <li>Your Wallet and Transactions pages refresh automatically.</li>
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

        {/* Section 6: Tech Stack */}
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
                <span className="arch-stack__value">Python, FastAPI, LangChain</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">AI Model</span>
                <span className="arch-stack__value">Gemini 2.5 Flash (via HKBU GenAI API)</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">Market Data</span>
                <span className="arch-stack__value">CCXT &rarr; Binance (real-time, no API key needed)</span>
              </div>
              <div className="arch-stack__row">
                <span className="arch-stack__label">Database</span>
                <span className="arch-stack__value">MongoDB Atlas (cloud)</span>
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
