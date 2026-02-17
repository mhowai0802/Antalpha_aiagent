import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './chatSlice';
import walletReducer from './walletSlice';
import transactionsReducer from './transactionsSlice';
import mcpReducer from './mcpSlice';

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    wallet: walletReducer,
    transactions: transactionsReducer,
    mcp: mcpReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
