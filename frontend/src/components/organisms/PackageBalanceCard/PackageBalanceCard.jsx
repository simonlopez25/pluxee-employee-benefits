import { BenefitBalanceRow } from '../../molecules/BenefitBalanceRow/BenefitBalanceRow'
import './PackageBalanceCard.css'

export function PackageBalanceCard({ packageBalance }) {
  const assigned = Number(packageBalance.assigned)

  return (
    <section className="package-balance-card">
      <header className="package-balance-card__header">
        <div>
          <h2 className="package-balance-card__title">{packageBalance.package_name}</h2>
          <p className="package-balance-card__subtitle">Paquete asignado</p>
        </div>
        <div className="package-balance-card__total">
          <span className="package-balance-card__total-label">Total asignado</span>
          <span className="package-balance-card__total-amount">
            {assigned.toLocaleString('es-ES', { minimumFractionDigits: 2 })} €
          </span>
        </div>
      </header>

      <div className="package-balance-card__benefits">
        {packageBalance.benefits.map((benefit) => (
          <BenefitBalanceRow
            key={benefit.benefit_id}
            benefit={benefit}
            packageAssigned={assigned}
          />
        ))}
      </div>
    </section>
  )
}