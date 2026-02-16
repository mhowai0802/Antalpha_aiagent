import { fetchBalance } from '../store/walletSlice';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import './WalletPage.scss';

export default function WalletPage() {
  const dispatch = useAppDispatch();
  const { assets, loading, error } = useAppSelector((s) => s.wallet);

  const entries = Object.entries(assets ?? {}).filter(([, v]) => v > 0);

  return (
    <div className="wallet">
      <div className="wallet-header">
        <span>Wallet</span>
        <button
          className="wallet-header__refresh"
          onClick={() => dispatch(fetchBalance())}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <div className="wallet-content">
        <div className="wallet-card">
          <div className="wallet-card__title">Balance</div>
          {error && <div className="wallet-error">Error: {error}</div>}
          {!error && entries.length === 0 && !loading && (
            <div className="wallet-empty">No assets</div>
          )}
          {entries.map(([asset, balance]) => (
            <div key={asset} className="wallet-row">
              <span className="wallet-row__asset">{asset}</span>
              <span className="wallet-row__balance">
                {asset === 'USD'
                  ? `$${Number(balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
                  : Number(balance).toFixed(8)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
