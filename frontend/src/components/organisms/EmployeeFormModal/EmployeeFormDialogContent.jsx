import { useState } from 'react'
import { EmployeeFormFields } from './EmployeeFormFields'
import { EmployeeCreateFields } from './EmployeeCreateFields'
import { EmployeeEditFields } from './EmployeeEditFields'
import { EmployeeDepartmentField } from './EmployeeDepartmentField'
import { EmployeeModalHeader } from './EmployeeModalHeader'
import { EmployeeModalFooter } from './EmployeeModalFooter'
import { validateCreateForm, validateEditForm } from './EmployeeFormValidation'

export function EmployeeFormDialogContent({
  mode,
  onClose,
  onSubmit,
  initialData,
  isSubmitting,
  apiError,
  departments = [],
}) {
  const isCreate = mode === 'create'
  const [fullName, setFullName] = useState(initialData?.fullName || '')
  const [email, setEmail] = useState(initialData?.email || '')
  const [temporaryPassword, setTemporaryPassword] = useState('')
  const [departmentId, setDepartmentId] = useState(
    initialData?.departmentId ?? null,
  )
  const [role, setRole] = useState(initialData?.role || 'EMPLOYEE')
  const [validationError, setValidationError] = useState('')
  const [errorField, setErrorField] = useState(null)

  const departmentRequired = isCreate || role === 'EMPLOYEE'
  const groupOptions = isCreate
    ? departments.filter((department) => department.isActive !== false)
    : departments

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

    const validation = isCreate
      ? validateCreateForm({
          fullName,
          email,
          temporaryPassword,
          departmentId,
        })
      : validateEditForm({
          fullName,
          email,
          role,
          departmentId,
          departmentRequired,
        })

    if (validation) {
      setFieldError(validation.field, validation.message)
      return
    }

    clearValidationError()

    if (isCreate) {
      onSubmit({
        fullName: trimmedFullName,
        email: trimmedEmail,
        temporaryPassword,
        departmentId: Number(departmentId),
      })
      return
    }

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
      <EmployeeModalHeader
        isCreate={isCreate}
        onClose={onClose}
        isSubmitting={isSubmitting}
      />

      <form onSubmit={handleSubmit} className="employeeModalForm">
        <div className="employeeModalBody">
          {apiError && (
            <div className="employeeModalAlert" role="alert">
              <span className="employeeModalAlertIcon">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm0 13a1 1 0 1 1 0-2 1 1 0 0 1 0 2zm0-9a1 1 0 0 1 1 1v5a1 1 0 1 1-2 0V2a1 1 0 0 1 1-1z" />
                </svg>
              </span>
              <span className="employeeModalAlertText">{apiError}</span>
            </div>
          )}

          <EmployeeFormFields
            fullName={fullName}
            email={email}
            isSubmitting={isSubmitting}
            errorField={errorField}
            validationError={validationError}
            onFullNameChange={setFullName}
            onEmailChange={setEmail}
            onClearError={clearValidationError}
          />

          {isCreate && (
            <EmployeeCreateFields
              temporaryPassword={temporaryPassword}
              onTemporaryPasswordChange={setTemporaryPassword}
              isSubmitting={isSubmitting}
              errorField={errorField}
              validationError={validationError}
              onClearError={clearValidationError}
            />
          )}

          {!isCreate && (
            <EmployeeEditFields
              role={role}
              onRoleChange={handleRoleChange}
              isSubmitting={isSubmitting}
            />
          )}

          <EmployeeDepartmentField
            departmentId={departmentId}
            departmentRequired={departmentRequired}
            groupOptions={groupOptions}
            onDepartmentChange={setDepartmentId}
            isSubmitting={isSubmitting}
            errorField={errorField}
            validationError={validationError}
            onClearError={clearValidationError}
          />
        </div>

        <EmployeeModalFooter
          isCreate={isCreate}
          isSubmitting={isSubmitting}
          onClose={onClose}
        />
      </form>
    </div>
  )
}