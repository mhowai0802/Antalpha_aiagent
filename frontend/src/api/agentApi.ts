/**
 * API service for crypto agent backend.
 */
const API_BASE =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? '/api' : 'http://localhost:8000');

export interface ChatResponse {
  response: string;
  user_id: string;
}

export interface BalanceResponse {
  user_id: string;
  assets: Record<string, number>;
}

export interface Transaction {
  _id: string;
  user_id: string;
  type: string;
  symbol: string;
  amount: number;
  price: number;
  usd_value: number;
  timestamp: string;
}

export interface TransactionsResponse {
  user_id: string;
  transactions: Transaction[];
}

export async function chat(
  message: string,
  userId = 'user_default'
): Promise<ChatResponse> {
  const url = `${API_BASE}/chat`;
  console.log('[agentApi] chat POST to:', url);
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, user_id: userId }),
  });
  console.log('[agentApi] chat response status:', res.status);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  console.log('[agentApi] chat response data:', data);
  return data;
}

export async function getBalance(
  userId = 'user_default'
): Promise<BalanceResponse> {
  const res = await fetch(`${API_BASE}/balance/${userId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getTransactions(
  userId = 'user_default',
  limit = 20
): Promise<TransactionsResponse> {
  const res = await fetch(`${API_BASE}/transactions/${userId}?limit=${limit}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
