import { useEffect, useState } from 'react'
import { PackageBalanceCard } from '../../components/organisms/PackageBalanceCard'
import { getMyBalance } from '../../services/balanceService'
import './EmployeePackagesPage.css'

export function EmployeePackagesPage() {
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
        if (!cancelled) setError('No se pudieron cargar tus beneficios.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) return <p className="employee-packages__state">Cargando tus beneficios…</p>
  if (error) return <p className="employee-packages__state employee-packages__state--error">{error}</p>
  if (!balance) return null

  const sortedPackages = [...balance.packages].sort(
    (a, b) => Number(b.assigned) - Number(a.assigned)
  )

  return (
    <div className="employee-packages">
      <header className="employee-packages__header">
        <div>
          <h1>Beneficios y paquetes</h1>
          <p className="employee-packages__subtitle">Lo que tienes a tu disposición este año.</p>
        </div>
      </header>

      <div className="employee-packages__list">
        {sortedPackages.length === 0 ? (
          <p className="employee-packages__state">No tienes paquetes asignados.</p>
        ) : (
          sortedPackages.map((pkg) => (
            <PackageBalanceCard key={pkg.package_id} packageBalance={pkg} />
          ))
        )}
      </div>
    </div>
  )
}