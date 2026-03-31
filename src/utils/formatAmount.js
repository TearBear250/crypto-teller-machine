export function formatAmount(amount) {
  if (amount < 1) return `$${Number(amount).toFixed(2)}`
  return `$${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 0 })}`
}
