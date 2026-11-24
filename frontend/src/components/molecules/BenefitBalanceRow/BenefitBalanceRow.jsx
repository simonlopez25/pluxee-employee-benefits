import { Icon } from '../../atoms/Icon'
import { ProgressBar } from '../ProgressBar'
import './BenefitBalanceRow.css'

const getIconNameByBenefitName = (name = '') => {
  const normalized = name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  if (normalized.includes('comida') || normalized.includes('restaurante')) return 'restaurant'
  if (normalized.includes('transporte') || normalized.includes('viaje')) return 'transport'
  if (normalized.includes('formacion') || normalized.includes('educacion') || normalized.includes('curso')) return 'training'
  if (normalized.includes('salud') || normalized.includes('medico') || normalized.includes('seguro')) return 'health'
  if (normalized.includes('guarderia') || normalized.includes('hijo') || normalized.includes('infantil')) return 'daycare'
  return 'catalog'
}

export function BenefitBalanceRow({ benefit, packageAssigned }) {
  const iconName = getIconNameByBenefitName(benefit.benefit_name)

  // El backend devuelve available y consumed por beneficio.
  // El assigned (total) es del paquete.
  const consumed = Number(benefit.consumed)
  const available = Number(benefit.available)

  // La barra se calcula sobre el total del paquete (packageAssigned)
  // para reflejar el consumo proporcional dentro de ese paquete.
  const ratio = packageAssigned > 0 ? Math.min(consumed / packageAssigned, 1) : 0

  return (
    <div className="benefit-balance-row">
      <div className="benefit-balance-row__icon-wrapper">
        <Icon name={iconName} size={20} />
      </div>

      <div className="benefit-balance-row__content">
        <div className="benefit-balance-row__header">
          <div className="benefit-balance-row__info">
            <span className="benefit-balance-row__name">{benefit.benefit_name}</span>
            {/* Descripción simulada, ya que el backend no la devuelve en este endpoint */}
            <span className="benefit-balance-row__desc">
              {benefit.is_basic ? 'Beneficio básico' : 'Beneficio flexible'}
            </span>
          </div>

          <div className="benefit-balance-row__amounts">
            <span className="benefit-balance-row__available">
              {available.toLocaleString('es-ES', { minimumFractionDigits: 2 })} € disponibles
            </span>
          </div>
        </div>

        <div className="benefit-balance-row__progress">
          <ProgressBar value={ratio * 100} showLabel={false} />
        </div>
      </div>
    </div>
  )
}