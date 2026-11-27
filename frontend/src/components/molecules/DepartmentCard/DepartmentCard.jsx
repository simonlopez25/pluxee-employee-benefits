import { Badge } from '../../atoms/Badge/Badge'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon'
import './DepartmentCard.css'

const formatEmployeeLabel = (count = 0) => {
  const safeCount = Number(count) || 0
  return `${safeCount} ${safeCount === 1 ? 'empleado' : 'empleados'}`
}

const formatPackagesSummary = (packages = []) => {
  if (!Array.isArray(packages) || packages.length === 0) {
    return { visibleNames: [], extraCount: 0, isEmpty: true }
  }

  return {
    visibleNames: packages.slice(0, 2).map((pkg) => pkg.name),
    extraCount: Math.max(0, packages.length - 2),
    isEmpty: false,
  }
}

const formatBudgetLabel = (monthlyBudget, currency) => {
  const amount = monthlyBudget?.allocatedAmount ?? monthlyBudget?.amount
  if (amount === undefined || amount === null || Number.isNaN(Number(amount))) {
    return 'Sin presupuesto'
  }

  const formattedAmount = Number(amount).toLocaleString('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return `${formattedAmount} ${currency || 'EUR'}`
}

export function DepartmentCard({ department, onEdit }) {
  const {
    name,
    currency,
    isActive,
    employeeCount = 0,
    packages = [],
    monthlyBudget = null,
  } = department

  const cardStatusClass = isActive ? 'departmentCardActive' : 'departmentCardInactive'
  const { visibleNames, extraCount, isEmpty: noPackages } = formatPackagesSummary(packages)
  const budgetLabel = formatBudgetLabel(monthlyBudget, currency)

  return (
    <article className={`departmentCard ${cardStatusClass}`}>
      <header className="departmentCardHeader">
        <div className="departmentCardIconWrapper">
          <Icon name="groups" size={22} />
        </div>
        <div className="departmentCardBadges">
          <Badge variant="default">{currency}</Badge>
          <Badge variant={isActive ? 'active' : 'inactive'}>
            {isActive ? 'Activo' : 'Inactivo'}
          </Badge>
        </div>
      </header>

      <div className="departmentCardBody">
        <h3 className="departmentCardTitle">{name}</h3>

        <div className="departmentCardMeta">
          <div className="departmentCardMetaRow">
            <span className="departmentCardMetaLabel">Empleados</span>
            <span className="departmentCardMetaValue">
              {formatEmployeeLabel(employeeCount)}
            </span>
          </div>

          <div className="departmentCardMetaRow">
            <span className="departmentCardMetaLabel">Paquetes</span>
            <span className="departmentCardMetaValue">
              {noPackages ? (
                'Sin paquetes'
              ) : (
                <>
                  {visibleNames.join(', ')}
                  {extraCount > 0 ? ` +${extraCount}` : ''}
                </>
              )}
            </span>
          </div>

          <div className="departmentCardMetaRow">
            <span className="departmentCardMetaLabel">Presupuesto</span>
            <span className="departmentCardMetaValue">{budgetLabel}</span>
          </div>
        </div>
      </div>

      <footer className="departmentCardFooter">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(department)}
          icon={<Icon name="edit" size={14} />}
        >
          Editar
        </Button>
      </footer>
    </article>
  )
}