import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function PasswordChangeGuard() {
  const { mustChangePassword } = useAuth()
  if (mustChangePassword) {
    return <Navigate to="/change-password" replace />
  }
  return <Outlet />
}

export default PasswordChangeGuard
