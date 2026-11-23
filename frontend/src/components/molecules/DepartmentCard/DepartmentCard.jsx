import { Badge } from '../../atoms/Badge'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import './DepartmentCard.css'

export function DepartmentCard({ department, onEdit }) {
  const { name, currency, isActive } = department

  const cardStatusClass = isActive ? 'departmentCardActive' : 'departmentCardInactive'

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