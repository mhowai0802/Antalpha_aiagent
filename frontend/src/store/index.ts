import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './chatSlice';
import walletReducer from './walletSlice';
import transactionsReducer from './transactionsSlice';

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    wallet: walletReducer,
    transactions: transactionsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
