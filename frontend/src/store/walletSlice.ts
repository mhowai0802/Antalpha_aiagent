import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { getBalance } from '../api/agentApi';

const userId = 'user_default';

interface WalletState {
  assets: Record<string, number>;
  loading: boolean;
  error: string | null;
}

export const fetchBalance = createAsyncThunk(
  'wallet/fetchBalance',
  async () => {
    const data = await getBalance(userId);
    return data.assets;
  }
);

const walletSlice = createSlice({
  name: 'wallet',
  initialState: {
    assets: {},
    loading: false,
    error: null,
  } as WalletState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBalance.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBalance.fulfilled, (state, action) => {
        state.loading = false;
        state.assets = action.payload ?? {};
      })
      .addCase(fetchBalance.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Unknown error';
      });
  },
});

export default walletSlice.reducer;
