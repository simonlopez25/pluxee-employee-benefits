export function EmployeeDepartmentField({
  departmentId,
  departmentRequired,
  groupOptions,
  onDepartmentChange,
  isSubmitting,
  errorField,
  validationError,
  onClearError,
}) {
  return (
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
          onDepartmentChange(event.target.value || null)
          onClearError()
        }}
        className={`employeeModalInput ${errorField === 'department' ? 'employeeModalInputError' : ''}`}
        disabled={isSubmitting || !departmentRequired}
      >
        <option value="">Seleccionar departamento</option>
        {groupOptions.map((department) => (
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
  )
}