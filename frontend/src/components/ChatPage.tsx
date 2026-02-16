import { useState, useRef, useEffect } from 'react';
import Markdown from 'react-markdown';
import { Bot, ArrowUp } from 'lucide-react';
import { sendMessage, addUserMessage, clearMessages } from '../store/chatSlice';
import { fetchBalance } from '../store/walletSlice';
import { fetchTransactions } from '../store/transactionsSlice';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import './ChatPage.scss';

export default function ChatPage() {
  const [input, setInput] = useState('');
  const dispatch = useAppDispatch();
  const { messages, loading } = useAppSelector((s) => s.chat);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // After agent replies, refresh wallet & transactions in store
  const messageCount = messages.length;
  useEffect(() => {
    if (messageCount >= 2) {
      const last = messages[messageCount - 1];
      if (last.role === 'assistant') {
        dispatch(fetchBalance());
        dispatch(fetchTransactions());
      }
    }
    // Only trigger when messageCount changes, not the messages array reference
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messageCount]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const msg = input.trim();
    console.log('[ChatPage] handleSend called, msg:', msg, 'loading:', loading);
    if (!msg || loading) return;
    dispatch(addUserMessage(msg));
    setInput('');
    console.log('[ChatPage] dispatching sendMessage...');
    dispatch(sendMessage(msg))
      .then((result: unknown) => console.log('[ChatPage] sendMessage resolved:', result))
      .catch((err: unknown) => console.error('[ChatPage] sendMessage rejected:', err));
  };

  const empty = messages.length === 0;
  const canSend = input.trim() && !loading;

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
            {messages.map((m, i) => (
              <div
                key={i}
                className={`chat-bubble ${m.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--agent'}`}
              >
                {m.role === 'assistant' ? (
                  <Markdown>{m.content}</Markdown>
                ) : (
                  m.content
                )}
              </div>
            ))}
            {loading && <div className="chat-thinking">Thinking...</div>}
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
