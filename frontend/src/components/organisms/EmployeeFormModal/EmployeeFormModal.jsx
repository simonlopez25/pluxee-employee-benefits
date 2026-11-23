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

  const departmentRequired = role === 'EMPLOYEE'

  const handleRoleChange = (event) => {
    const newRole = event.target.value
    setRole(newRole)
    if (newRole === 'ADMIN') {
      setDepartmentId(null)
    }
    if (validationError) {
      setValidationError('')
    }
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const trimmedFullName = fullName.trim()
    const trimmedEmail = email.trim()

    if (!trimmedFullName) {
      setValidationError('El nombre completo es obligatorio')
      return
    }

    if (trimmedFullName.length > 120) {
      setValidationError('El nombre no puede superar los 120 caracteres')
      return
    }

    if (!trimmedEmail) {
      setValidationError('El correo electrónico es obligatorio')
      return
    }

    if (!EMAIL_REGEX.test(trimmedEmail)) {
      setValidationError('El correo electrónico no tiene un formato válido')
      return
    }

    if (departmentRequired && !departmentId) {
      setValidationError('Debe seleccionar un departamento para el empleado')
      return
    }

    if (!departmentRequired && departmentId) {
      setValidationError('Un administrador no puede tener departamento asignado')
      return
    }

    setValidationError('')
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
                if (validationError) {
                  setValidationError('')
                }
              }}
              className={`employeeModalInput ${validationError ? 'employeeModalInputError' : ''}`}
              disabled={isSubmitting}
              autoFocus
            />
            {validationError && (
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
                if (validationError) {
                  setValidationError('')
                }
              }}
              className={`employeeModalInput ${validationError ? 'employeeModalInputError' : ''}`}
              disabled={isSubmitting}
            />
            {validationError && (
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
                if (validationError) {
                  setValidationError('')
                }
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
            {departmentRequired && validationError && !departmentId && (
              <span className="employeeModalErrorMessage">
                Selecciona un departamento
              </span>
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
