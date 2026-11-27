import { Icon } from '../../atoms/Icon/Icon'

export function EmployeeModalHeader({
  isCreate,
  onClose,
  isSubmitting,
}) {
  return (
    <header className="employeeModalHeader">
      <div className="employeeModalHeaderInfo">
        <h2 id="employeeModalTitle" className="employeeModalTitle">
          {isCreate ? 'Dar de alta empleado' : 'Editar empleado'}
        </h2>
        <p className="employeeModalSubtitle">
          {isCreate
            ? 'Asigna un correo, una contraseña temporal y un grupo. El empleado deberá cambiar su contraseña al iniciar sesión.'
            : 'Modifica los datos del empleado. Los cambios se guardan sin eliminar su registro ni sus históricos de gastos y asignaciones.'}
        </p>
      </div>
      <button
        type="button"
        className="employeeModalCloseButton"
        onClick={onClose}
        disabled={isSubmitting}
        aria-label="Cerrar modal"
      >
        <Icon name="close" size={18} />
      </button>
    </header>
  )
}