import { useEffect, useState } from 'react';
import { Terminal, RefreshCw, Trash2, Clock, Radio } from 'lucide-react';
import { fetchMcpLog, clearMcpLog, fetchMcpHistory, deleteMcpHistory } from '../store/mcpSlice';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import type { McpLogEntry } from '../api/agentApi';
import './MCPInspectorPage.scss';

type Tab = 'live' | 'history';

function McpCard({ entry, index }: { entry: McpLogEntry; index: number }) {
  const params = (entry.request as Record<string, unknown>).params as Record<string, unknown> | undefined;
  const toolName = params?.name ?? 'unknown';
  const ts = entry.timestamp
    ? new Date(entry.timestamp * 1000).toLocaleTimeString()
    : '';

  return (
    <div className="mcp-card">
      <div className="mcp-card__header">
        <code className="mcp-card__tool">{String(toolName)}</code>
        {ts && <span className="mcp-card__time">{ts}</span>}
      </div>
      <div className="mcp-card__panels">
        <div className="mcp-card__panel">
          <span className="mcp-card__label">Request</span>
          <pre className="mcp-card__json">
            {JSON.stringify(entry.request, null, 2)}
          </pre>
        </div>
        <div className="mcp-card__panel">
          <span className="mcp-card__label">Response</span>
          <pre className="mcp-card__json">
            {JSON.stringify(entry.response, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ tab }: { tab: Tab }) {
  return (
    <div className="mcp-empty">
      <Terminal size={36} />
      <div className="mcp-empty__title">
        {tab === 'live' ? 'No MCP calls yet' : 'No history'}
      </div>
      <div className="mcp-empty__subtitle">
        {tab === 'live'
          ? 'Send a message in Chat to see MCP JSON-RPC requests and responses here.'
          : 'MCP call history will appear here once you start chatting.'}
      </div>
    </div>
  );
}

export default function MCPInspectorPage() {
  const dispatch = useAppDispatch();
  const { log, loading, history, historyLoading, historyHasMore } = useAppSelector((s) => s.mcp);
  const [tab, setTab] = useState<Tab>('live');

  useEffect(() => {
    if (tab === 'live') {
      dispatch(fetchMcpLog());
    } else {
      dispatch(fetchMcpHistory(false));
    }
  }, [dispatch, tab]);

  const toolCalls = (entries: McpLogEntry[]) =>
    entries.filter((e) => e.type === 'tools/call');

  const liveEntries = toolCalls(log);
  const historyEntries = toolCalls(history);

  return (
    <div className="mcp">
      <div className="mcp-header">
        <span className="mcp-header__title">MCP Inspector</span>
        <div className="mcp-header__actions">
          {tab === 'live' && (
            <>
              <button className="mcp-header__btn" onClick={() => dispatch(fetchMcpLog())}>
                <RefreshCw size={14} className={loading ? 'spin' : ''} />
                Refresh
              </button>
              <button className="mcp-header__btn" onClick={() => dispatch(clearMcpLog())}>
                <Trash2 size={14} />
                Clear
              </button>
            </>
          )}
          {tab === 'history' && (
            <>
              <button className="mcp-header__btn" onClick={() => dispatch(fetchMcpHistory(false))}>
                <RefreshCw size={14} className={historyLoading ? 'spin' : ''} />
                Refresh
              </button>
              <button className="mcp-header__btn" onClick={() => dispatch(deleteMcpHistory())}>
                <Trash2 size={14} />
                Clear History
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="mcp-tabs">
        <button
          className={`mcp-tabs__tab ${tab === 'live' ? 'mcp-tabs__tab--active' : ''}`}
          onClick={() => setTab('live')}
        >
          <Radio size={14} />
          Live
        </button>
        <button
          className={`mcp-tabs__tab ${tab === 'history' ? 'mcp-tabs__tab--active' : ''}`}
          onClick={() => setTab('history')}
        >
          <Clock size={14} />
          History
        </button>
      </div>

      <div className="mcp-content">
        {tab === 'live' && (
          liveEntries.length === 0 ? (
            <EmptyState tab="live" />
          ) : (
            <div className="mcp-list">
              <p className="mcp-intro">
                Current session — showing MCP calls from this browser session only.
              </p>
              {liveEntries.map((entry, i) => (
                <McpCard key={i} entry={entry} index={i} />
              ))}
            </div>
          )
        )}

        {tab === 'history' && (
          historyEntries.length === 0 && !historyLoading ? (
            <EmptyState tab="history" />
          ) : (
            <div className="mcp-list">
              <p className="mcp-intro">
                All MCP calls stored in MongoDB — persists across server restarts.
              </p>
              {historyEntries.map((entry, i) => (
                <McpCard key={i} entry={entry} index={i} />
              ))}
              {historyHasMore && (
                <button
                  className="mcp-load-more"
                  onClick={() => dispatch(fetchMcpHistory(true))}
                  disabled={historyLoading}
                >
                  {historyLoading ? 'Loading...' : 'Load more'}
                </button>
              )}
            </div>
          )
        )}
      </div>
    </div>
  );
}
