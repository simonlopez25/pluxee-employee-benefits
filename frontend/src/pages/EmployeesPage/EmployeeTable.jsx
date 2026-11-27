import { formatDate, STATUS_LABELS } from './EmployeesPage.utils'
import { Badge } from '../../components/atoms/Badge/Badge'
import { Button } from '../../components/atoms/Button/Button'
import { Icon } from '../../components/atoms/Icon/Icon'

export function EmployeeTable({
  employees,
  departments,
  currentUserId,
  isSubmitting,
  isDeactivating,
  onEdit,
  onDeactivate,
}) {
  const isCurrentAdmin = (employeeId) => currentUserId === employeeId

  const getDepartmentName = (departmentId) => {
    if (!departmentId) return '—'
    const dept = departments.find((d) => d.id === departmentId)
    return dept ? dept.name : '-'
  }

  if (!employees.length) return null

  return (
    <div className="employeesTableWrapper">
      <table className="employeesTable">
        <thead>
          <tr>
            <th className="employeesTableCell">Empleado</th>
            <th className="employeesTableCell">Correo</th>
            <th className="employeesTableCell">Rol</th>
            <th className="employeesTableCell">Departamento</th>
            <th className="employeesTableCell">Estado</th>
            <th className="employeesTableCell">Fecha de baja</th>
            <th className="employeesTableCell employeesTableActions">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.id} className="employeesTableRow">
              <td className="employeesTableCell">
                <span className="employeesTableName">
                  {employee.fullName}
                </span>
              </td>
              <td className="employeesTableCell">{employee.email}</td>
              <td className="employeesTableCell">
                <Badge
                  variant={employee.role === 'ADMIN' ? 'basic' : 'default'}
                >
                  {employee.role === 'ADMIN' ? 'Administrador' : 'Empleado'}
                </Badge>
              </td>
              <td className="employeesTableCell">
                {getDepartmentName(employee.departmentId)}
              </td>
              <td className="employeesTableCell">
                <Badge
                  variant={employee.isActive ? 'active' : 'inactive'}
                >
                  {STATUS_LABELS[employee.isActive]}
                </Badge>
              </td>
              <td className="employeesTableCell">
                {employee.isActive ? (
                  <span className="employeesTableNone">—</span>
                ) : (
                  <span>{formatDate(employee.deactivatedAt)}</span>
                )}
              </td>
              <td className="employeesTableCell employeesTableActions">
                <EmployeeActions
                  employee={employee}
                  isCurrentAdmin={isCurrentAdmin(employee.id)}
                  isSubmitting={isSubmitting}
                  isDeactivating={isDeactivating}
                  onEdit={onEdit}
                  onDeactivate={onDeactivate}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function EmployeeActions({
  employee,
  isCurrentAdmin,
  isSubmitting,
  isDeactivating,
  onEdit,
  onDeactivate,
}) {
  if (!employee.isActive) {
    return <span className="employeesActionsNone">Inactivo</span>
  }

  if (isCurrentAdmin) {
    return (
      <>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(employee)}
          disabled={isSubmitting || isDeactivating}
          icon={<Icon name="edit" size={14} />}
        >
          Editar
        </Button>
        <span className="employeesActionsNote">Tú (administrador)</span>
      </>
    )
  }

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onEdit(employee)}
        disabled={isSubmitting || isDeactivating}
        icon={<Icon name="edit" size={14} />}
      >
        Editar
      </Button>
      <Button
        variant="danger"
        size="sm"
        onClick={() => onDeactivate(employee)}
        disabled={isSubmitting || isDeactivating}
        icon={<Icon name="close" size={14} />}
      >
        Dar de baja
      </Button>
    </>
  )
}