import { Badge } from '../../atoms/Badge/Badge'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import './BenefitCard.css'

const getIconNameByBenefitName = (name = '') => {
  const normalized = name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  if (normalized.includes('comida') || normalized.includes('restaurante')) {
    return 'restaurant'
  }
  if (normalized.includes('transporte') || normalized.includes('viaje')) {
    return 'transport'
  }
  if (normalized.includes('formacion') || normalized.includes('educacion') || normalized.includes('curso')) {
    return 'training'
  }
  if (normalized.includes('salud') || normalized.includes('medico') || normalized.includes('seguro')) {
    return 'health'
  }
  if (normalized.includes('guarderia') || normalized.includes('hijo') || normalized.includes('infantil')) {
    return 'daycare'
  }
  return 'box'
}

export function BenefitCard({
  benefit,
  onEdit,
  onToggleStatus,
  isToggling = false,
}) {
  const { id, name, description, isBasic, isActive } = benefit
  const iconName = getIconNameByBenefitName(name)

  const cardStatusClass = isActive ? 'benefitCardActive' : 'benefitCardInactive'

  return (
    <article className={`benefitCard ${cardStatusClass}`}>
      <header className="benefitCardHeader">
        <div className="benefitCardIconWrapper">
          <Icon name={iconName} size={22} className="benefitCardIcon" />
        </div>
        <div className="benefitCardBadges">
          {isBasic && <Badge variant="basic">Básico</Badge>}
          <Badge variant={isActive ? 'active' : 'inactive'}>
            {isActive ? 'Activo' : 'Inactivo'}
          </Badge>
        </div>
      </header>

      <div className="benefitCardBody">
        <h3 className="benefitCardTitle">{name}</h3>
        <p className="benefitCardDescription">
          {description || 'Sin descripción especificada'}
        </p>
      </div>

      <footer className="benefitCardFooter">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(benefit)}
          icon={<Icon name="edit" size={14} />}
        >
          Editar
        </Button>

        <Button
          variant={isActive ? 'ghost' : 'secondary'}
          size="sm"
          disabled={isToggling}
          onClick={() => onToggleStatus(id, !isActive)}
        >
          {isToggling ? 'Actualizando...' : isActive ? 'Desactivar' : 'Activar'}
        </Button>
      </footer>
    </article>
  )
}

