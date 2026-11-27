import { Link } from 'react-router-dom'
import './EmployeeHomePage.css'
import { useAuth } from '../../context/AuthContext'
import { EmployeeBalanceSummary } from '../../components/organisms/EmployeeBalanceSummary'
import { Icon } from '../../components/atoms/Icon'
import { useMyBalance } from '../../hooks/useMyBalance'

export function EmployeeHomePage() {
  const { user } = useAuth()
  const { balance, error, loading } = useMyBalance(
    'No se pudo cargar tu saldo. Inténtalo de nuevo.'
  )

  if (loading) return <p className="employee-home__state">Cargando tu saldo…</p>
  if (error) return <p className="employee-home__state employee-home__state--error">{error}</p>
  if (!balance) return null

  return (
    <div className="employee-home">
      <header className="employee-home__header">
        <div>
          <h1>Hola, {user?.full_name?.split(' ')[0] || 'empleado'} 👋</h1>
          <p className="employee-home__subtitle">Este es el estado de tus beneficios este mes.</p>
        </div>
      </header>

      <div className="employee-home__content">
        <div className="employee-home__main-col">
          <EmployeeBalanceSummary balance={balance} />
        </div>

        <aside className="employee-home__side-col">
          <Link to="/empleado/beneficios" className="employee-home__action-card">
            <div className="employee-home__action-card-icon">
              <Icon name="gift" size={20} />
            </div>
            <span className="employee-home__action-card-label">
              Mis beneficios
            </span>
          </Link>
        </aside>
      </div>
    </div>
  )
}