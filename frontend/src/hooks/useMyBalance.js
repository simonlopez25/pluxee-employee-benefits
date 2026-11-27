import { useEffect, useState } from 'react'
import { getMyBalance } from '../services/balanceService'

export function useMyBalance(errorMessage) {
  const [balance, setBalance] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    getMyBalance()
      .then((data) => {
        if (!cancelled) setBalance(data)
      })
      .catch(() => {
        if (!cancelled) setError(errorMessage)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [errorMessage])

  return { balance, error, loading }
}