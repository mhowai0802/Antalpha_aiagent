import { useState, useRef, useEffect } from 'react';
import Markdown from 'react-markdown';
import { Bot, ArrowUp, ChevronDown, ChevronRight, ArrowRight } from 'lucide-react';
import { sendMessage, addUserMessage, clearMessages, ChatMessage } from '../store/chatSlice';
import { fetchBalance } from '../store/walletSlice';
import { fetchTransactions } from '../store/transactionsSlice';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import type { AgentStep } from '../api/agentApi';
import './ChatPage.scss';

/* ── One row in the translation pipeline (left → right chat style) ── */

function PipelineRow({ label, left, right, leftColor, rightColor, expandLeft, expandRight }: {
  label: string;
  left: React.ReactNode;
  right: React.ReactNode;
  leftColor: string;
  rightColor: string;
  expandLeft?: React.ReactNode;
  expandRight?: React.ReactNode;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="prow">
      <div className="prow__label">{label}</div>
      <div className="prow__columns">
        <div className={`prow__cell prow__cell--left`} style={{ borderLeftColor: leftColor }}>
          {left}
          {expanded && expandLeft && (
            <div className="prow__detail">{expandLeft}</div>
          )}
        </div>
        <div className="prow__arrow"><ArrowRight size={14} /></div>
        <div className={`prow__cell prow__cell--right`} style={{ borderLeftColor: rightColor }}>
          {right}
          {expanded && expandRight && (
            <div className="prow__detail">{expandRight}</div>
          )}
        </div>
      </div>
      {(expandLeft || expandRight) && (
        <button className="prow__toggle" onClick={() => setExpanded(!expanded)}>
          {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          {expanded ? 'Hide' : 'Show'} full JSON
        </button>
      )}
    </div>
  );
}

/* ── Full translation pipeline for one tool call ── */

function TranslationPipeline({ step, userMessage, aiReply }: {
  step: AgentStep;
  userMessage: string;
  aiReply: string;
}) {
  const toolArgs = step.tool_input || {};

  return (
    <div className="pipeline">
      {/* Row 1: User question → AI structured decision */}
      <PipelineRow
        label="1. AI understands your question"
        left={
          <div className="prow__quote">&ldquo;{userMessage}&rdquo;</div>
        }
        right={
          <div>
            <div className="prow__kv">
              <span className="prow__key">Tool:</span>
              <code className="prow__val">{step.tool}</code>
            </div>
            <div className="prow__kv">
              <span className="prow__key">Args:</span>
              <code className="prow__val">{JSON.stringify(toolArgs)}</code>
            </div>
          </div>
        }
        leftColor="#2563eb"
        rightColor="#a855f7"
      />

      {/* Row 2: MCP request → MCP response */}
      <PipelineRow
        label="2. MCP Server processes (JSON-RPC)"
        left={
          <pre className="prow__json prow__json--compact">
{`{
  "method": "tools/call",
  "params": {
    "name": "${step.tool}",
    "arguments": ${JSON.stringify(toolArgs)}
  }
}`}
          </pre>
        }
        right={
          <pre className="prow__json prow__json--compact">{step.tool_output}</pre>
        }
        leftColor="#06b6d4"
        rightColor="#22c55e"
        expandLeft={
          <pre className="prow__json">{JSON.stringify(step.mcp_request, null, 2)}</pre>
        }
        expandRight={
          <pre className="prow__json">{JSON.stringify(step.mcp_response, null, 2)}</pre>
        }
      />

      {/* Row 3: Raw data → AI natural language reply */}
      <PipelineRow
        label="3. AI composes reply"
        left={
          <pre className="prow__json prow__json--compact">{
            step.tool_output.length > 120
              ? step.tool_output.slice(0, 120) + '...'
              : step.tool_output
          }</pre>
        }
        right={
          <div className="prow__quote">{
            aiReply.length > 150
              ? aiReply.slice(0, 150) + '...'
              : aiReply
          }</div>
        }
        leftColor="#22c55e"
        rightColor="#f59e0b"
      />
    </div>
  );
}

/* ── Always-visible reasoning panel ── */

function ReasoningPanel({ steps, userMessage, aiReply }: {
  steps: AgentStep[];
  userMessage: string;
  aiReply: string;
}) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="reasoning">
      {steps.map((s, i) => (
        <TranslationPipeline
          key={i}
          step={s}
          userMessage={userMessage}
          aiReply={aiReply}
        />
      ))}
    </div>
  );
}

/* ── Main chat page ── */

export default function ChatPage() {
  const [input, setInput] = useState('');
  const dispatch = useAppDispatch();
  const { messages, loading } = useAppSelector((s) => s.chat);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const messageCount = messages.length;
  useEffect(() => {
    if (messageCount >= 2) {
      const last = messages[messageCount - 1];
      if (last.role === 'assistant') {
        dispatch(fetchBalance());
        dispatch(fetchTransactions());
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messageCount]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const msg = input.trim();
    if (!msg || loading) return;
    dispatch(addUserMessage(msg));
    setInput('');
    dispatch(sendMessage(msg));
  };

  const empty = messages.length === 0;
  const canSend = input.trim() && !loading;

  const getUserMessageBefore = (idx: number): string => {
    for (let j = idx - 1; j >= 0; j--) {
      if (messages[j].role === 'user') return messages[j].content;
    }
    return '';
  };

  return (
    <div className="chat">
      <div className="chat-header">
        <span className="chat-header__title">Chat</span>
        {messages.length > 0 && (
          <button className="chat-header__clear" onClick={() => dispatch(clearMessages())}>
            Clear
          </button>
        )}
      </div>

      <div className="chat-messages">
        {empty ? (
          <div className="chat-empty">
            <div className="chat-empty__icon"><Bot size={40} /></div>
            <div className="chat-empty__title">Crypto Agent</div>
            <div className="chat-empty__subtitle">
              Ask about prices, buy crypto, or check your balance
            </div>
          </div>
        ) : (
          <div className="chat-list">
            {messages.map((m: ChatMessage, i: number) => (
              <div key={i} className={`chat-row ${m.role === 'user' ? 'chat-row--user' : 'chat-row--agent'}`}>
                <div className={`chat-bubble ${m.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--agent'}`}>
                  {m.role === 'assistant' && (
                    <div className="chat-bubble__badge"><Bot size={12} /> Agent</div>
                  )}
                  {m.role === 'assistant' ? (
                    <Markdown>{m.content}</Markdown>
                  ) : (
                    m.content
                  )}
                </div>
                {m.role === 'assistant' && m.steps && m.steps.length > 0 && (
                  <ReasoningPanel
                    steps={m.steps}
                    userMessage={getUserMessageBefore(i)}
                    aiReply={m.content}
                  />
                )}
              </div>
            ))}
            {loading && (
              <div className="chat-row chat-row--agent">
                <div className="chat-thinking">Thinking...</div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="chat-input-bar">
        <form onSubmit={handleSend} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Send a message..."
            disabled={loading}
            className="chat-input-form__input"
          />
          <button
            type="submit"
            disabled={!canSend}
            className={`chat-input-form__send ${canSend ? 'chat-input-form__send--active' : 'chat-input-form__send--disabled'}`}
          >
            <ArrowUp size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
