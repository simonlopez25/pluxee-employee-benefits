import { ProgressBar } from '../../molecules/ProgressBar/ProgressBar'
import './EmployeeBalanceSummary.css'

export function EmployeeBalanceSummary({ balance }) {
  const assigned = Number(balance.assigned_total)
  const consumed = Number(balance.consumed_total)
  const available = Number(balance.available_total)
  const ratio = assigned > 0 ? Math.min(consumed / assigned, 1) : 0

  return (
    <section className="employee-balance-summary">
      <article className="employee-balance-summary__hero">
        <span className="employee-balance-summary__label">Saldo disponible</span>
        <strong className="employee-balance-summary__amount">
          {available.toLocaleString('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}{' '}
          €
        </strong>

        <div className="employee-balance-summary__progress-wrapper">
          <ProgressBar
            value={ratio * 100}
            showLabel={false}
            variant="inverted"
          />
        </div>

        <div className="employee-balance-summary__metrics">
          <div>
            <span className="employee-balance-summary__metric-label">Asignado</span>
            <span className="employee-balance-summary__metric-value">
              {assigned.toLocaleString('es-ES', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}{' '}
              €
            </span>
          </div>
          <div>
            <span className="employee-balance-summary__metric-label">Consumido</span>
            <span className="employee-balance-summary__metric-value">
              {consumed.toLocaleString('es-ES', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}{' '}
              €
            </span>
          </div>
        </div>
      </article>
    </section>
  )
}