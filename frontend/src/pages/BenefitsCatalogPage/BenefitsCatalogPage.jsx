import { AdminLayout } from '../../components/templates/AdminLayout'
import { BenefitsCatalogSection } from '../../components/organisms/BenefitsCatalogSection'
import './BenefitsCatalogPage.css'

export function BenefitsCatalogPage() {
  return (
    <AdminLayout>
      <div className="benefitsPageContainer">
        <BenefitsCatalogSection />

        <section className="packagesIntegrationSection">
          <div className="packagesIntegrationHeader">
            <h2 className="packagesIntegrationTitle">Paquetes</h2>
            <span className="packagesIntegrationBadge">HU-10 Próximamente</span>
          </div>

          <div className="packagesPlaceholderGrid">
            <div className="packagePlaceholderCard">
              <h3 className="packagePlaceholderTitle">Paquete Bienestar Creativo</h3>
              <p className="packagePlaceholderSubtitle">Para equipos de Marketing y Diseño.</p>
              <div className="packagePlaceholderMeta">
                <span>Restaurante · 1.320 €</span>
                <span>Transporte · 1.080 €</span>
              </div>
            </div>

            <div className="packagePlaceholderCard">
              <h3 className="packagePlaceholderTitle">Paquete Familia</h3>
              <p className="packagePlaceholderSubtitle">Conciliación para empleados con hijos.</p>
              <div className="packagePlaceholderMeta">
                <span>Restaurante · 1.320 €</span>
                <span>Guardería · 2.400 €</span>
              </div>
            </div>

            <div className="packagePlaceholderCard">
              <h3 className="packagePlaceholderTitle">Paquete Esencial</h3>
              <p className="packagePlaceholderSubtitle">Cobertura básica para toda la plantilla.</p>
              <div className="packagePlaceholderMeta">
                <span>Restaurante · 1.320 €</span>
                <span>Transporte · 720 €</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </AdminLayout>
  )
}

