import { AdminLayout } from '../../components/templates/AdminLayout'
import { BenefitsCatalogSection } from '../../components/organisms/BenefitsCatalogSection'
import { PackagesSection } from '../../components/organisms/PackagesSection'
import './BenefitsCatalogPage.css'

export function BenefitsCatalogPage() {
  return (
    <AdminLayout>
      <div className="benefitsPageContainer">
        <BenefitsCatalogSection />

        <PackagesSection />
      </div>
    </AdminLayout>
  )
}