const COINS = [
  { id: 'BCH', label: 'Bitcoin Cash', symbol: 'BCH', color: '#4CAF50', enabled: true },
  { id: 'LTC', label: 'Litecoin', symbol: 'LTC', color: '#607D8B', enabled: true },
  { id: 'DOGE', label: 'Dogecoin', symbol: 'DOGE', color: '#FFC107', enabled: true },
  { id: 'XRP', label: 'XRP', symbol: 'XRP', color: '#2196F3', enabled: false },
  { id: 'SOL', label: 'Solana', symbol: 'SOL', color: '#9C27B0', enabled: false },
]

export default function HomeScreen({ onSelect }) {
  return (
    <div className="screen home-screen">
      <h1 className="screen-title">Crypto Teller Machine</h1>
      <p className="screen-subtitle">Select a cryptocurrency to purchase</p>
      <div className="coin-grid">
        {COINS.map((coin) => (
          <button
            key={coin.id}
            className={`coin-btn${coin.enabled ? '' : ' disabled'}`}
            style={{ '--coin-color': coin.color }}
            onClick={() => coin.enabled && onSelect(coin.id)}
            disabled={!coin.enabled}
            aria-label={coin.enabled ? `Select ${coin.label}` : `${coin.label} coming soon`}
          >
            <span className="coin-symbol">{coin.symbol}</span>
            <span className="coin-label">{coin.label}</span>
            {!coin.enabled && <span className="coming-soon">Coming Soon</span>}
          </button>
        ))}
      </div>
    </div>
  )
}
