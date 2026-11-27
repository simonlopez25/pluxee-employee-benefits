import { Button } from '../../components/atoms/Button/Button'
import { Icon } from '../../components/atoms/Icon'

export function EmployeesEmptyState({ onCreate }) {
  return (
    <div className="employeesEmptyState">
      <div className="employeesEmptyIconWrapper">
        <Icon name="groups" size={32} />
      </div>
      <h3 className="employeesEmptyTitle">
        No hay empleados registrados
      </h3>
      <p className="employeesEmptySubtitle">
        La plantilla está vacía. Da de alta al primer empleado para
        asignarle su grupo y sus beneficios.
      </p>
      <Button
        variant="secondary"
        size="sm"
        onClick={onCreate}
        icon={<Icon name="plus" size={16} />}
      >
        Dar de alta empleado
      </Button>
    </div>
  )
}