import { AdminLayout } from '../components/templates/AdminLayout'
import './PlaceholderPage.css'

export function PlaceholderPage({ title, description }) {
  return (
    <AdminLayout>
      <div className="placeholderPageContainer">
        <header className="placeholderPageHeader">
          <h1 className="placeholderPageTitle">{title}</h1>
          <p className="placeholderPageSubtitle">{description}</p>
        </header>

        <div className="placeholderPageContent">
          <div className="placeholderPageCard">
            <h2 className="placeholderCardHeading">Módulo en construcción</h2>
            <p className="placeholderCardText">
              Esta sección formará parte de las siguientes subtareas del proyecto.
            </p>
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
