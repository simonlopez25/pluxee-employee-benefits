import { BenefitTotalsSummary } from '../../components/organisms/BenefitTotalsSummary'
import { PackageBalanceCard } from '../../components/organisms/PackageBalanceCard'
import { useMyBalance } from '../../hooks/useMyBalance'
import './EmployeePackagesPage.css'

export function EmployeePackagesPage() {
  const { balance, error, loading } = useMyBalance(
    'No se pudieron cargar tus beneficios.'
  )

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
          <p className="employee-packages__subtitle">Lo que tienes a tu disposición este mes.</p>
        </div>
      </header>

      <div className="employee-packages__list">
        <BenefitTotalsSummary benefits={balance.by_benefit} />

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