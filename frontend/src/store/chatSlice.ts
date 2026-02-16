import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { chat } from '../api/agentApi';

const userId = 'user_default';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatState {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
}

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message: string) => {
    console.log('[chatSlice] sendMessage thunk START:', message);
    try {
      const data = await chat(message, userId);
      console.log('[chatSlice] sendMessage thunk OK:', data.response.substring(0, 80));
      return data.response;
    } catch (err) {
      console.error('[chatSlice] sendMessage thunk ERROR:', err);
      throw err;
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    loading: false,
    error: null,
  } as ChatState,
  reducers: {
    addUserMessage: (state, action) => {
      state.messages.push({ role: 'user', content: action.payload });
    },
    clearMessages: (state) => {
      state.messages = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        console.log('[chatSlice] reducer: PENDING');
        state.loading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        console.log('[chatSlice] reducer: FULFILLED, payload length:', action.payload?.length);
        state.loading = false;
        state.messages.push({ role: 'assistant', content: action.payload });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        console.log('[chatSlice] reducer: REJECTED', action.error.message);
        state.loading = false;
        state.error = action.error.message ?? 'Unknown error';
        state.messages.push({
          role: 'assistant',
          content: `Error: ${action.error.message}`,
        });
      });
  },
});

export const { addUserMessage, clearMessages } = chatSlice.actions;
export default chatSlice.reducer;
