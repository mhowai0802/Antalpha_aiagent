import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getMcpLog, getMcpLogHistory, deleteMcpLog, McpLogEntry } from '../api/agentApi';

const userId = 'user_default';

interface McpState {
  log: McpLogEntry[];
  loading: boolean;
  history: McpLogEntry[];
  historyLoading: boolean;
  historySkip: number;
  historyHasMore: boolean;
  error: string | null;
}

const PAGE_SIZE = 50;

export const fetchMcpLog = createAsyncThunk('mcp/fetchLog', async () => {
  const data = await getMcpLog(userId);
  return data.mcp_calls;
});

export const fetchMcpHistory = createAsyncThunk(
  'mcp/fetchHistory',
  async (loadMore: boolean, { getState }) => {
    const state = getState() as { mcp: McpState };
    const skip = loadMore ? state.mcp.historySkip : 0;
    const data = await getMcpLogHistory(userId, PAGE_SIZE, skip);
    return { entries: data.mcp_calls, loadMore };
  }
);

export const deleteMcpHistory = createAsyncThunk('mcp/deleteHistory', async () => {
  const result = await deleteMcpLog(userId);
  return result.deleted;
});

const mcpSlice = createSlice({
  name: 'mcp',
  initialState: {
    log: [],
    loading: false,
    history: [],
    historyLoading: false,
    historySkip: 0,
    historyHasMore: true,
    error: null,
  } as McpState,
  reducers: {
    clearMcpLog: (state) => {
      state.log = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Live log
      .addCase(fetchMcpLog.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMcpLog.fulfilled, (state, action) => {
        state.loading = false;
        state.log = action.payload;
      })
      .addCase(fetchMcpLog.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch MCP log';
      })
      // History
      .addCase(fetchMcpHistory.pending, (state) => {
        state.historyLoading = true;
        state.error = null;
      })
      .addCase(fetchMcpHistory.fulfilled, (state, action) => {
        state.historyLoading = false;
        const { entries, loadMore } = action.payload;
        if (loadMore) {
          state.history = [...state.history, ...entries];
        } else {
          state.history = entries;
        }
        state.historySkip = (loadMore ? state.historySkip : 0) + entries.length;
        state.historyHasMore = entries.length >= PAGE_SIZE;
      })
      .addCase(fetchMcpHistory.rejected, (state, action) => {
        state.historyLoading = false;
        state.error = action.error.message ?? 'Failed to fetch history';
      })
      // Delete history
      .addCase(deleteMcpHistory.fulfilled, (state) => {
        state.history = [];
        state.historySkip = 0;
        state.historyHasMore = true;
      });
  },
});

export const { clearMcpLog } = mcpSlice.actions;
export default mcpSlice.reducer;
