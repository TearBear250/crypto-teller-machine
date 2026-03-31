export default function DenominationScreen({ coin, denominations, onSelect, onBack }) {
  const formatAmount = (amount) => {
    if (amount < 1) return `$${amount.toFixed(2)}`
    return `$${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 0 })}`
  }

  return (
    <div className="screen denom-screen">
      <button className="back-btn" onClick={onBack} aria-label="Back to coin selection">
        ← Back
      </button>
      <h1 className="screen-title">Select Amount — {coin}</h1>

      <section className="denom-section">
        <h2 className="section-heading">Coins</h2>
        <div className="denom-grid">
          {denominations.coins.map((amount) => (
            <button
              key={amount}
              className="denom-btn"
              onClick={() => onSelect(amount)}
              aria-label={`Select ${formatAmount(amount)}`}
            >
              {formatAmount(amount)}
            </button>
          ))}
        </div>
      </section>

      <section className="denom-section">
        <h2 className="section-heading">Bills</h2>
        <div className="denom-grid">
          {denominations.bills.map((amount) => (
            <button
              key={amount}
              className="denom-btn"
              onClick={() => onSelect(amount)}
              aria-label={`Select ${formatAmount(amount)}`}
            >
              {formatAmount(amount)}
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
