import { useState } from 'react'
import HomeScreen from './components/HomeScreen'
import DenominationScreen from './components/DenominationScreen'
import VoucherScreen from './components/VoucherScreen'
import denominations from '../denominations.json'

export default function App() {
  const [screen, setScreen] = useState('home')
  const [selectedCoin, setSelectedCoin] = useState(null)
  const [selectedDenom, setSelectedDenom] = useState(null)

  if (screen === 'home') {
    return (
      <HomeScreen
        onSelect={(coin) => {
          setSelectedCoin(coin)
          setScreen('denom')
        }}
      />
    )
  }
  if (screen === 'denom') {
    return (
      <DenominationScreen
        coin={selectedCoin}
        denominations={denominations}
        onSelect={(d) => {
          setSelectedDenom(d)
          setScreen('voucher')
        }}
        onBack={() => setScreen('home')}
      />
    )
  }
  if (screen === 'voucher') {
    return (
      <VoucherScreen
        coin={selectedCoin}
        denomination={selectedDenom}
        onBack={() => setScreen('home')}
      />
    )
  }
  return null
}
