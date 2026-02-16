import { fetchTransactions } from '../store/transactionsSlice';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import './TransactionsPage.scss';

export default function TransactionsPage() {
  const dispatch = useAppDispatch();
  const { list, loading, error } = useAppSelector((s) => s.transactions);

  return (
    <div className="txns">
      <div className="txns-header">
        <span>Transaction Records</span>
        <button
          className="txns-header__refresh"
          onClick={() => dispatch(fetchTransactions())}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
      <div className="txns-content">
        <div className="txns-card">
          {error && <div className="txns-error">Error: {error}</div>}
          {!error && !loading && list.length === 0 && (
            <div className="txns-empty">No transactions yet</div>
          )}
          {list.length > 0 && (
            <>
              {/* Desktop table */}
              <table className="txns-table txns-table--desktop">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Symbol</th>
                    <th>Amount</th>
                    <th>Price</th>
                    <th>USD Value</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((t) => (
                    <tr key={t._id}>
                      <td>
                        <span className={`txns-badge ${t.type === 'BUY' ? 'txns-badge--buy' : 'txns-badge--sell'}`}>
                          {t.type}
                        </span>
                      </td>
                      <td className="txns-symbol">{t.symbol}</td>
                      <td className="txns-mono">{t.amount.toFixed(8)}</td>
                      <td className="txns-muted">${t.price.toLocaleString()}</td>
                      <td className="txns-muted">${t.usd_value.toLocaleString()}</td>
                      <td className="txns-time">{new Date(t.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Mobile card list */}
              <div className="txns-mobile-list">
                {list.map((t) => (
                  <div key={t._id} className="txns-mobile-item">
                    <div className="txns-mobile-item__top">
                      <span className={`txns-badge ${t.type === 'BUY' ? 'txns-badge--buy' : 'txns-badge--sell'}`}>
                        {t.type}
                      </span>
                      <span className="txns-symbol">{t.symbol}</span>
                      <span className="txns-mobile-item__value">${t.usd_value.toLocaleString()}</span>
                    </div>
                    <div className="txns-mobile-item__details">
                      <span className="txns-mono">Amt: {t.amount.toFixed(8)}</span>
                      <span className="txns-muted">@ ${t.price.toLocaleString()}</span>
                    </div>
                    <div className="txns-time">{new Date(t.timestamp).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
