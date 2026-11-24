import { NavLink } from 'react-router-dom'
import { Icon } from '../../atoms/Icon'
import { useAuth } from '../../../context/AuthContext'
import '../AdminSidebar/AdminSidebar.css'

export function EmployeeSidebar() {
  const { user, logout } = useAuth()

  const menuItems = [
    { key: 'inicio', label: 'Inicio', path: '/empleado', icon: 'home' },
    { key: 'beneficios', label: 'Beneficios y paquetes', path: '/empleado/beneficios', icon: 'catalog' },
  ]

  const initials = user?.full_name
    ?.split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'U'

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

      <div className="sidebarSectionLabel">MI ESPACIO</div>

      <nav className="sidebarNav">
        {menuItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end
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
        <button type="button" className="sidebarSwitchButton" onClick={logout}>
          <Icon name="close" size={16} />
          <span>Cerrar sesión</span>
        </button>

        <div className="sidebarUserProfile">
          <div className="sidebarUserAvatar">{initials}</div>
          <div className="sidebarUserInfo">
            <span className="sidebarUserName">{user?.full_name ?? 'Empleado'}</span>
            <span className="sidebarUserRole">Empleado</span>
          </div>
        </div>
      </div>
    </aside>
  )
}