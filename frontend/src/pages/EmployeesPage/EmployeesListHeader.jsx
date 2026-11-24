export function EmployeesListHeader({ count }) {
  if (count === 0) return null

  return (
    <div className="employeesListHeader">
      <span className="employeesCountBadge">
        <span className="employeesCountNumber">{count}</span>
        <span className="employeesCountLabel">
          {count === 1 ? 'empleado' : 'empleados'}
        </span>
      </span>
    </div>
  )
}