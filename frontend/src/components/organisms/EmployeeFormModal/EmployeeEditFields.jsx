import { ROLE_OPTIONS } from './EmployeeFormValidation'

export function EmployeeEditFields({
  role,
  onRoleChange,
  isSubmitting,
}) {
  return (
    <div className="employeeModalField">
      <label htmlFor="employeeRole" className="employeeModalLabel">
        Rol <span className="employeeModalRequiredMark">*</span>
      </label>
      <select
        id="employeeRole"
        value={role}
        onChange={onRoleChange}
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
  )
}