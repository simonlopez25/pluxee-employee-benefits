import { AdminSidebar } from '../../organisms/AdminSidebar/AdminSidebar'
import './AdminLayout.css'

export function AdminLayout({ children }) {
  return (
    <div className="adminLayoutContainer">
      <AdminSidebar />
      <main className="adminLayoutMain">
        <div className="adminLayoutContentWrapper">{children}</div>
      </main>
    </div>
  )
}

