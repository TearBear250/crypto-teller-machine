import { useEffect, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { generateAddress } from '../services/walletService'
import { formatAmount } from '../utils/formatAmount'

const COIN_LABELS = {
  BCH: 'Bitcoin Cash',
  LTC: 'Litecoin',
  DOGE: 'Dogecoin',
}

export default function VoucherScreen({ coin, denomination, onBack }) {
  const [addressData, setAddressData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    try {
      const data = generateAddress(coin)
      setAddressData(data)
    } catch (err) {
      setError(err.message)
    }
  }, [coin])

  const handlePrint = () => {
    if (window.electronAPI?.printPage) {
      window.electronAPI.printPage()
    } else {
      window.print()
    }
  }

  return (
    <div className="screen voucher-screen">
      <div className="no-print">
        <button className="back-btn" onClick={onBack} aria-label="Back to home">
          ← Start Over
        </button>
      </div>

      <div className="voucher" id="voucher-content">
        <div className="voucher-header">
          <h1 className="voucher-title">Crypto Teller Machine</h1>
          <h2 className="voucher-coin">
            {COIN_LABELS[coin] || coin} ({coin})
          </h2>
          <p className="voucher-amount">{formatAmount(denomination)}</p>
        </div>

        {error ? (
          <p className="error-msg">Error generating address: {error}</p>
        ) : addressData ? (
          <div className="voucher-body">
            <div className="qr-container">
              <QRCodeSVG value={addressData.address} size={200} level="M" />
            </div>
            <p className="address-label">Send {coin} to this address:</p>
            <p className="address-text">{addressData.address}</p>
          </div>
        ) : (
          <p className="loading-msg">Generating address…</p>
        )}

        <div className="voucher-footer">
          <p>Generated: {new Date().toLocaleString()}</p>
        </div>
      </div>

      <div className="no-print">
        <button className="print-btn" onClick={handlePrint} disabled={!addressData}>
          🖨 Print Voucher
        </button>
      </div>
    </div>
  )
}
