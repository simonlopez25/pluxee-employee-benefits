import { NavLink } from 'react-router-dom'
import { Icon } from '../../atoms/Icon'
import './AdminSidebar.css'

export function AdminSidebar() {
  const menuItems = [
    { key: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { key: 'groups', label: 'Grupos', path: '/groups', icon: 'groups' },
    { key: 'employees', label: 'Empleados', path: '/admin/employees', icon: 'groups' },
    { key: 'budgets', label: 'Presupuestos', path: '/budgets', icon: 'budget' },
    { key: 'catalog', label: 'Catálogo', path: '/catalog', icon: 'catalog' },
    { key: 'assignments', label: 'Asignaciones', path: '/assignments', icon: 'assignments' },
    { key: 'expenses', label: 'Gestión de gastos', path: '/expenses', icon: 'expenses' },
  ]

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
        {menuItems.map((item) => (
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
        <button type="button" className="sidebarSwitchButton">
          <Icon name="switchUser" size={16} />
          <span>Ver como empleado</span>
        </button>

        <div className="sidebarUserProfile">
          <div className="sidebarUserAvatar">EN</div>
          <div className="sidebarUserInfo">
            <span className="sidebarUserName">Elena Navarro</span>
            <span className="sidebarUserRole">Administradora de RR. ...</span>
          </div>
        </div>
      </div>
    </aside>
  )
}

