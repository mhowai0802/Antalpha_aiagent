import { useState } from 'react';
import { Provider } from 'react-redux';
import { Menu } from 'lucide-react';
import { store } from './store';
import { fetchBalance } from './store/walletSlice';
import { fetchTransactions } from './store/transactionsSlice';
import Sidebar from './components/Sidebar';
import ChatPage from './components/ChatPage';
import WalletPage from './components/WalletPage';
import TransactionsPage from './components/TransactionsPage';
import ArchitecturePage from './components/ArchitecturePage';
import './index.css';
import './App.scss';

export type Page = 'chat' | 'wallet' | 'transactions' | 'architecture';

// Fetch initial data into Redux store on app startup
store.dispatch(fetchBalance());
store.dispatch(fetchTransactions());

export default function App() {
  const [page, setPage] = useState<Page>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleNavigate = (p: Page) => {
    setPage(p);
    setSidebarOpen(false);
  };

  return (
    <Provider store={store}>
      <div className="app-root">
        {sidebarOpen && (
          <div className="app-overlay" onClick={() => setSidebarOpen(false)} />
        )}
        <Sidebar
          activePage={page}
          onNavigate={handleNavigate}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
        <main className="app-main">
          <div className="mobile-topbar">
            <button className="mobile-topbar__menu" onClick={() => setSidebarOpen(true)}>
              <Menu size={22} />
            </button>
            <span className="mobile-topbar__title">Crypto Agent</span>
          </div>
          {page === 'chat' && <ChatPage />}
          {page === 'wallet' && <WalletPage />}
          {page === 'transactions' && <TransactionsPage />}
          {page === 'architecture' && <ArchitecturePage />}
        </main>
      </div>
    </Provider>
  );
}
