import { NavLink } from 'react-router-dom'
import { Icon } from '../../atoms/Icon/Icon'
import { useAuth } from '../../../context/AuthContext'
import './EmployeeSidebar.css'

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
    <aside className="employee-sidebar">
      <div className="employee-sidebar__header">
        <div className="employee-sidebar__brand">
          <div className="employee-sidebar__brand-badge">P</div>
          <div className="employee-sidebar__brand-title">
            <span className="employee-sidebar__brand-bold">pluxee</span>
            <span className="employee-sidebar__brand-dot">.</span>
            <span className="employee-sidebar__brand-regular">benefits</span>
          </div>
        </div>
      </div>

      <div className="employee-sidebar__section-label">MI ESPACIO</div>

      <nav className="employee-sidebar__nav">
        {menuItems.map((item) => (
          <NavLink
            key={item.key}
            to={item.path}
            end
            className={({ isActive }) =>
              `employee-sidebar__item-base ${isActive ? 'employee-sidebar__item--active' : 'employee-sidebar__item'}`
            }
          >
            <span className="employee-sidebar__icon">
              <Icon name={item.icon} size={18} />
            </span>
            <span className="employee-sidebar__label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="employee-sidebar__footer">
        <button type="button" className="employee-sidebar__logout" onClick={logout}>
          <Icon name="close" size={16} />
          <span>Cerrar sesión</span>
        </button>

        <div className="employee-sidebar__profile">
          <div className="employee-sidebar__avatar">{initials}</div>
          <div className="employee-sidebar__user">
            <span className="employee-sidebar__user-name">{user?.full_name ?? 'Empleado'}</span>
            <span className="employee-sidebar__user-role">Empleado</span>
          </div>
        </div>
      </div>
    </aside>
  )
}