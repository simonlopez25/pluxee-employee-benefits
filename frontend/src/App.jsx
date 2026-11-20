import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { BenefitsCatalogPage } from './pages/BenefitsCatalogPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import './styles/App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="appWrapper">
        <Routes>
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
          <Route
            path="/budgets"
            element={
              <PlaceholderPage
                title="Presupuestos"
                description="Control de presupuestos asignados por departamento."
              />
            }
          />
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
          <Route path="*" element={<Navigate to="/catalog" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
