import { Outlet } from 'react-router-dom'
import { EmployeeSidebar } from '../../organisms/EmployeeSidebar/EmployeeSidebar'
import './EmployeeLayout.css'

export function EmployeeLayout() {
  return (
    <div className="employeeLayout">
      <EmployeeSidebar />
      <main className="employeeLayoutContent">
        <Outlet />
      </main>
    </div>
  )
}