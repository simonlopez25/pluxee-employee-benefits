import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import PasswordChangeGuard from './components/PasswordChangeGuard'
import ChangePasswordForm from './components/ChangePasswordForm/ChangePasswordForm'
import Login from './pages/Login'
import Home from './pages/Home'
import Profile from './pages/Profile'
import { BenefitsCatalogPage } from './pages/BenefitsCatalogPage'
import { BudgetsPage } from './pages/BudgetsPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import './styles/App.css'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="appWrapper">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/change-password" element={<ChangePasswordForm isForced={true} onSuccess={() => window.location.assign('/')} />} />
            <Route element={<ProtectedRoute role="ADMIN" />}>
              <Route element={<PasswordChangeGuard />}>
                <Route path="/admin" element={<Home />} />
                <Route path="/perfil" element={<Profile />} />
              </Route>
            </Route>
            <Route element={<ProtectedRoute role="EMPLOYEE" />}>
              <Route element={<PasswordChangeGuard />}>
                <Route path="/empleado" element={<Home />} />
                <Route path="/perfil" element={<Profile />} />
              </Route>
            </Route>
            <Route path="/" element={<Navigate to="/catalog" replace />} />
            <Route path="/catalog" element={<BenefitsCatalogPage />} />
            <Route
              path="/dashboard"
              element={
                <PlaceholderPage
                  title="Dashboard"
                  description="Resumen general de beneficios y métricas clave."
                />
              }
            />
            <Route
              path="/groups"
              element={
                <PlaceholderPage
                  title="Grupos"
                  description="Gestión de departamentos y grupos de la organización."
                />
              }
            />
            <Route path="/budgets" element={<BudgetsPage />} />
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
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App