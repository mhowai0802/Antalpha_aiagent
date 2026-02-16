import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getTransactions, type Transaction } from '../api/agentApi';

const userId = 'user_default';

interface TransactionsState {
  list: Transaction[];
  loading: boolean;
  error: string | null;
}

export const fetchTransactions = createAsyncThunk(
  'transactions/fetchTransactions',
  async (limit = 20) => {
    const data = await getTransactions(userId, limit);
    return data.transactions;
  }
);

const transactionsSlice = createSlice({
  name: 'transactions',
  initialState: {
    list: [],
    loading: false,
    error: null,
  } as TransactionsState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchTransactions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTransactions.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload ?? [];
      })
      .addCase(fetchTransactions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Unknown error';
      });
  },
});

export default transactionsSlice.reducer;
