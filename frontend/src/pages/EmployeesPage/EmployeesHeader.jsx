import { Button } from '../../components/atoms/Button/Button'
import { Icon } from '../../components/atoms/Icon/Icon'

export function EmployeesHeader({ onCreate }) {
  return (
    <header className="employeesHeader">
      <div className="employeesHeaderContent">
        <h1 className="employeesTitle">Empleados</h1>
        <p className="employeesSubtitle">
          Gestión de la plantilla: alta, edición de datos y baja lógica de
          empleados.
        </p>
      </div>
      <div className="employeesHeaderActions">
        <Button
          variant="secondary"
          size="sm"
          onClick={onCreate}
          icon={<Icon name="plus" size={16} />}
        >
          Dar de alta
        </Button>
      </div>
    </header>
  )
}