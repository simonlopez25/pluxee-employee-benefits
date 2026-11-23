import { NavLink } from 'react-router-dom'
import { useAuth } from '../../../context/AuthContext'
import { Icon } from '../../atoms/Icon'
import './AdminSidebar.css'

const ADMIN_MENU = [
  { key: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
  { key: 'groups', label: 'Grupos', path: '/groups', icon: 'groups' },
  { key: 'budgets', label: 'Presupuestos', path: '/budgets', icon: 'budget' },
  { key: 'catalog', label: 'Catálogo', path: '/catalog', icon: 'catalog' },
  { key: 'assignments', label: 'Asignaciones', path: '/assignments', icon: 'assignments' },
  { key: 'expenses', label: 'Gestión de gastos', path: '/expenses', icon: 'expenses' },
]

function getInitials(name = '') {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('')
}

export function AdminSidebar() {
  const { user, logout } = useAuth()
  const initials = getInitials(user?.full_name || user?.fullName || '')
  const roleLabel = user?.role === 'ADMIN' ? 'Administrador' : 'Empleado'

  return (
    <aside className="sidebarContainer">
      <div className="sidebarHeader">
        <div className="sidebarBrand">
          <div className="sidebarBrandBadge">P</div>
          <div className="sidebarBrandTitle">
            <span className="sidebarBrandBold">pluxee</span>
            <span className="sidebarBrandDot">.</span>
            <span className="sidebarBrandRegular">benefits</span>
          </div>
        </div>
      </div>

      <div className="sidebarSectionLabel">ADMINISTRACIÓN</div>

      <nav className="sidebarNav">
        {ADMIN_MENU.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            className={({ isActive }) =>
              `sidebarNavItemBase ${isActive ? 'sidebarNavItemActive' : 'sidebarNavItem'}`
            }
          >
            <span className="sidebarNavIcon">
              <Icon name={item.icon} size={18} />
            </span>
            <span className="sidebarNavLabel">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebarFooter">
  <button type="button" className="sidebarSwitchButton" style={{ justifyContent: 'center' }} onClick={logout}>
  <span>Cerrar sesión</span>
</button>

  <div className="sidebarUserProfile">
    <div className="sidebarUserAvatar">{initials || 'U'}</div>
    <div className="sidebarUserInfo">
      <span className="sidebarUserName">{user?.full_name || user?.fullName}</span>
      <span className="sidebarUserRole">{roleLabel}</span>
    </div>
  </div>
</div>
    </aside>
  )
}