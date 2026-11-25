import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import PasswordChangeGuard from './components/PasswordChangeGuard'
import ChangePasswordForm from './components/ChangePasswordForm/ChangePasswordForm'
import Login from './pages/Login'
import Home from './pages/Home'
import Profile from './pages/Profile'
import { BenefitsCatalogPage } from './pages/BenefitsCatalogPage'
import { BudgetsPage } from './pages/BudgetsPage'
import { GroupsPage } from './pages/GroupsPage'
import { EmployeesPage } from './pages/EmployeesPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import './styles/App.css'

function ChangePasswordRoute() {
  const { user } = useAuth()
  return (
    <ChangePasswordForm
      isForced={true}
      onSuccess={() =>
        window.location.assign(
          user?.role === 'ADMIN' ? '/dashboard' : '/empleado'
        )
      }
    />
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="appWrapper">
          <Routes>
            <Route path="/login" element={<Login />} />

            <Route element={<ProtectedRoute />}>
              <Route path="/change-password" element={<ChangePasswordRoute />} />
            </Route>

            <Route element={<ProtectedRoute role="ADMIN" />}>
              <Route element={<PasswordChangeGuard />}>
                <Route path="/admin" element={<Navigate to="/dashboard" replace />} />
                <Route path="/employees" element={<EmployeesPage />} />
                <Route path="/admin/employees" element={<Navigate to="/employees" replace />} />
                <Route
                  path="/dashboard"
                  element={
                    <PlaceholderPage
                      title="Dashboard"
                      description="Resumen general de beneficios y métricas clave."
                    />
                  }
                />
                <Route path="/groups" element={<GroupsPage />} />
                <Route path="/budgets" element={<BudgetsPage />} />
                <Route path="/catalog" element={<BenefitsCatalogPage />} />
                <Route
                  path="/assignments"
                  element={
                    <PlaceholderPage
                      title="Asignaciones"
                      description="Asignaciones de paquetes a empleados y equipos."
                    />
                  }
                />
                <Route
                  path="/expenses"
                  element={
                    <PlaceholderPage
                      title="Gestión de gastos"
                      description="Aprobación y seguimiento de solicitudes de gastos."
                    />
                  }
                />
              </Route>
            </Route>

            <Route element={<ProtectedRoute role="EMPLOYEE" />}>
              <Route element={<PasswordChangeGuard />}>
                <Route path="/empleado" element={<Home />} />
              </Route>
            </Route>

            <Route element={<ProtectedRoute />}>
              <Route element={<PasswordChangeGuard />}>
                <Route path="/perfil" element={<Profile />} />
              </Route>
            </Route>

            <Route path="/" element={<Navigate to="/catalog" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App