import { useState } from 'react'

export function EmployeeFormFields({
  initialData,
  isSubmitting,
  errorField,
  validationError,
  onFieldChange,
  onClearError,
}) {
  const [fullName, setFullName] = useState(initialData?.fullName || '')
  const [email, setEmail] = useState(initialData?.email || '')

  const handleFullNameChange = (event) => {
    setFullName(event.target.value)
    onFieldChange('fullName', event.target.value)
    onClearError()
  }

  const handleEmailChange = (event) => {
    setEmail(event.target.value)
    onFieldChange('email', event.target.value)
    onClearError()
  }

  return (
    <>
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
          onChange={handleFullNameChange}
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
          onChange={handleEmailChange}
          className={`employeeModalInput ${errorField === 'email' ? 'employeeModalInputError' : ''}`}
          disabled={isSubmitting}
        />
        {errorField === 'email' && (
          <span className="employeeModalErrorMessage">{validationError}</span>
        )}
      </div>
    </>
  )
}