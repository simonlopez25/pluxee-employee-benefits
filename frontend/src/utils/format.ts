export const formatCurrency = (
  amount: number | string,
  options: { currency?: string; style?: 'currency' | 'decimal' } = {}
): string => {
  const num = typeof amount === 'string' ? Number(amount) : amount
  const { currency = 'EUR', style = 'currency' } = options

  if (style === 'decimal') {
    return num.toLocaleString('es-ES', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  }

  return num.toLocaleString('es-ES', {
    style,
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}