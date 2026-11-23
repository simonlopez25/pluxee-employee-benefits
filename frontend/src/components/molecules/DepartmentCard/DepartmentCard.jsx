import { Badge } from '../../atoms/Badge'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import './DepartmentCard.css'

export function DepartmentCard({ department, onEdit }) {
  const { name, currency } = department

  return (
    <article className="departmentCard">
      <header className="departmentCardHeader">
        <h3 className="departmentCardTitle">{name}</h3>
        <Badge variant="default">{currency}</Badge>
      </header>

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
