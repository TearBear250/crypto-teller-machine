import { Buffer } from 'buffer'
if (typeof globalThis.Buffer === 'undefined') {
  globalThis.Buffer = Buffer
}

import * as bitcoin from 'bitcoinjs-lib'
import * as ecc from 'tiny-secp256k1'
import { ECPairFactory } from 'ecpair'

const ECPair = ECPairFactory(ecc)

const networks = {
  BCH: {
    messagePrefix: '\x18Bitcoin Signed Message:\n',
    bech32: 'bc',
    bip32: { public: 0x0488b21e, private: 0x0488ade4 },
    pubKeyHash: 0x00,
    scriptHash: 0x05,
    wif: 0x80,
  },
  LTC: {
    messagePrefix: '\x19Litecoin Signed Message:\n',
    bech32: 'ltc',
    bip32: { public: 0x019da462, private: 0x019d9cfe },
    pubKeyHash: 0x30,
    scriptHash: 0x32,
    wif: 0xb0,
  },
  DOGE: {
    messagePrefix: '\x19Dogecoin Signed Message:\n',
    bech32: 'doge',
    bip32: { public: 0x02facafd, private: 0x02fac398 },
    pubKeyHash: 0x1e,
    scriptHash: 0x16,
    wif: 0x9e,
  },
}

export function generateAddress(coin) {
  const network = networks[coin]
  if (!network) throw new Error(`Unsupported coin: ${coin}`)
  const keyPair = ECPair.makeRandom({ network })
  const { address } = bitcoin.payments.p2pkh({ pubkey: keyPair.publicKey, network })
  // Private key is intentionally not returned. Note: JavaScript does not support
  // explicit memory zeroing, so the keyPair will be garbage-collected by the runtime.
  return { address, coin }
}

export function generateAddressXRP() {
  // TODO: Implement XRP address generation using xrpl library
  throw new Error('XRP address generation is not yet implemented')
}

export function generateAddressSOL() {
  // TODO: Implement Solana address generation using @solana/web3.js
  throw new Error('SOL address generation is not yet implemented')
}
