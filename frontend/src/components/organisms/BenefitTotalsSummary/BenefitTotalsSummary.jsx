import './BenefitTotalsSummary.css'

const formatEuros = (value) =>
  `${Number(value).toLocaleString('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} €`

// Máximo que el empleado puede gastar hoy en cada beneficio (backend: by_benefit).
// Los importes se solapan si hay paquetes multibeneficio, por eso no se suman.
export function BenefitTotalsSummary({ benefits = [] }) {
  if (benefits.length === 0) return null

  return (
    <section className="benefit-totals" aria-labelledby="benefit-totals-title">
      <h2 id="benefit-totals-title" className="benefit-totals__title">
        Disponible por beneficio
      </h2>
      <p className="benefit-totals__note">
        Los paquetes multibeneficio comparten saldo: un gasto en uno de sus
        beneficios reduce lo disponible en los demás.
      </p>

      <ul className="benefit-totals__list">
        {benefits.map((benefit) => (
          <li key={benefit.benefit_id} className="benefit-totals__item">
            <span className="benefit-totals__name">{benefit.benefit_name}</span>
            <span className="benefit-totals__amount">
              {formatEuros(benefit.available)}
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}
