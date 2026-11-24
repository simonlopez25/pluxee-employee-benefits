export function EmployeeCreateFields({
  temporaryPassword,
  onTemporaryPasswordChange,
  isSubmitting,
  errorField,
  validationError,
  onClearError,
}) {
  return (
    <div className="employeeModalField">
      <label
        htmlFor="employeeTemporaryPassword"
        className="employeeModalLabel"
      >
        Contraseña temporal{' '}
        <span className="employeeModalRequiredMark">*</span>
      </label>
      <input
        id="employeeTemporaryPassword"
        type="password"
        maxLength={128}
        placeholder="Mínimo 10 caracteres"
        autoComplete="new-password"
        value={temporaryPassword}
        onChange={(event) => {
          onTemporaryPasswordChange(event.target.value)
          onClearError()
        }}
        className={`employeeModalInput ${errorField === 'temporaryPassword' ? 'employeeModalInputError' : ''}`}
        disabled={isSubmitting}
      />
      <p className="employeeModalFieldNote">
        El empleado deberá cambiarla al iniciar sesión.
      </p>
      {errorField === 'temporaryPassword' && (
        <span className="employeeModalErrorMessage">
          {validationError}
        </span>
      )}
    </div>
  )
}