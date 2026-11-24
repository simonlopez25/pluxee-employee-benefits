import { useEffect, useState } from 'react'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import './EmployeeFormModal.css'

const ROLE_OPTIONS = [
  { value: 'ADMIN', label: 'Administrador' },
  { value: 'EMPLOYEE', label: 'Empleado' },
]

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function EmployeeFormDialogContent({
  onClose,
  onSubmit,
  initialData,
  isSubmitting,
  apiError,
  departments = [],
}) {
  const [fullName, setFullName] = useState(initialData?.fullName || '')
  const [email, setEmail] = useState(initialData?.email || '')
  const [departmentId, setDepartmentId] = useState(
    initialData?.departmentId ?? null,
  )
  const [role, setRole] = useState(initialData?.role || 'EMPLOYEE')
  const [validationError, setValidationError] = useState('')
  const [errorField, setErrorField] = useState(null)

  const departmentRequired = role === 'EMPLOYEE'

  const clearValidationError = () => {
    setValidationError('')
    setErrorField(null)
  }

  const setFieldError = (field, message) => {
    setErrorField(field)
    setValidationError(message)
  }

  const handleRoleChange = (event) => {
    const newRole = event.target.value
    setRole(newRole)
    if (newRole === 'ADMIN') {
      setDepartmentId(null)
    }
    clearValidationError()
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const trimmedFullName = fullName.trim()
    const trimmedEmail = email.trim()

    if (!trimmedFullName) {
      setFieldError('fullName', 'El nombre completo es obligatorio')
      return
    }

    if (trimmedFullName.length > 120) {
      setFieldError('fullName', 'El nombre no puede superar los 120 caracteres')
      return
    }

    if (!trimmedEmail) {
      setFieldError('email', 'El correo electrónico es obligatorio')
      return
    }

    if (!EMAIL_REGEX.test(trimmedEmail)) {
      setFieldError('email', 'El correo electrónico no tiene un formato válido')
      return
    }

    if (departmentRequired && !departmentId) {
      setFieldError('department', 'Debe seleccionar un departamento para el empleado')
      return
    }

    if (!departmentRequired && departmentId) {
      setFieldError('department', 'Un administrador no puede tener departamento asignado')
      return
    }

    clearValidationError()
    onSubmit({
      fullName: trimmedFullName,
      email: trimmedEmail,
      departmentId: departmentRequired ? Number(departmentId) : null,
      role,
    })
  }

  return (
    <div
      className="employeeModalContainer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="employeeModalTitle"
      onClick={(event) => event.stopPropagation()}
    >
      <header className="employeeModalHeader">
        <div className="employeeModalHeaderInfo">
          <h2 id="employeeModalTitle" className="employeeModalTitle">
            Editar empleado
          </h2>
          <p className="employeeModalSubtitle">
            Modifica los datos del empleado. Los cambios se guardan sin eliminar
            su registro ni sus históricos de gastos y asignaciones.
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

      <form onSubmit={handleSubmit} className="employeeModalForm">
        <div className="employeeModalBody">
          {apiError && (
            <div className="employeeModalAlert" role="alert">
              <span className="employeeModalAlertIcon">
                <Icon name="close" size={16} />
              </span>
              <span className="employeeModalAlertText">{apiError}</span>
            </div>
          )}

          <div className="employeeModalField">
            <label htmlFor="employeeFullName" className="employeeModalLabel">
              Nombre completo <span className="employeeModalRequiredMark">*</span>
            </label>
            <input
              id="employeeFullName"
              type="text"
              maxLength={120}
              placeholder="Ej. Lucía García"
              value={fullName}
              onChange={(event) => {
                setFullName(event.target.value)
                clearValidationError()
              }}
              className={`employeeModalInput ${errorField === 'fullName' ? 'employeeModalInputError' : ''}`}
              disabled={isSubmitting}
              autoFocus
            />
            {errorField === 'fullName' && (
              <span className="employeeModalErrorMessage">{validationError}</span>
            )}
          </div>

          <div className="employeeModalField">
            <label htmlFor="employeeEmail" className="employeeModalLabel">
              Correo electrónico <span className="employeeModalRequiredMark">*</span>
            </label>
            <input
              id="employeeEmail"
              type="email"
              maxLength={150}
              placeholder="Ej. lucia.garcia@empresa.com"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value)
                clearValidationError()
              }}
              className={`employeeModalInput ${errorField === 'email' ? 'employeeModalInputError' : ''}`}
              disabled={isSubmitting}
            />
            {errorField === 'email' && (
              <span className="employeeModalErrorMessage">{validationError}</span>
            )}
          </div>

          <div className="employeeModalField">
            <label htmlFor="employeeRole" className="employeeModalLabel">
              Rol <span className="employeeModalRequiredMark">*</span>
            </label>
            <select
              id="employeeRole"
              value={role}
              onChange={handleRoleChange}
              className="employeeModalInput"
              disabled={isSubmitting}
            >
              {ROLE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="employeeModalField">
            <label htmlFor="employeeDepartment" className="employeeModalLabel">
              Departamento {departmentRequired && (
                <span className="employeeModalRequiredMark">*</span>
              )}
            </label>
            <select
              id="employeeDepartment"
              value={departmentId || ''}
              onChange={(event) => {
                setDepartmentId(event.target.value || null)
                clearValidationError()
              }}
              className="employeeModalInput"
              disabled={isSubmitting || !departmentRequired}
            >
              <option value="">Seleccionar departamento</option>
              {departments.map((department) => (
                <option key={department.id} value={department.id}>
                  {department.name}
                </option>
              ))}
            </select>
            {!departmentRequired && (
              <p className="employeeModalFieldNote">
                Los administradores no tienen departamento asignado.
              </p>
            )}
            {errorField === 'department' && (
              <span className="employeeModalErrorMessage">{validationError}</span>
            )}
          </div>
        </div>

        <footer className="employeeModalFooter">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="secondary"
            disabled={isSubmitting}
            icon={isSubmitting ? <Icon name="spinner" size={16} /> : null}
          >
            {isSubmitting ? 'Guardando...' : 'Guardar cambios'}
          </Button>
        </footer>
      </form>
    </div>
  )
}

export function EmployeeFormModal({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
  isSubmitting = false,
  apiError = null,
  departments = [],
}) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isOpen && !isSubmitting) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, isSubmitting, onClose])

  if (!isOpen) {
    return null
  }

  const formKey = `edit-${initialData?.id}`

  return (
    <div className="employeeModalBackdrop" onClick={onClose}>
      <EmployeeFormDialogContent
        key={formKey}
        onClose={onClose}
        onSubmit={onSubmit}
        initialData={initialData}
        isSubmitting={isSubmitting}
        apiError={apiError}
        departments={departments}
      />
    </div>
  )
}
