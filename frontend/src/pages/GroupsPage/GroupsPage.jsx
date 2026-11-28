import { AdminLayout } from '../../components/templates/AdminLayout/AdminLayout'
import { GroupsSection } from '../../components/organisms/GroupsSection/GroupsSection'
import './GroupsPage.css'

export function GroupsPage() {
  return (
    <AdminLayout>
      <div className="groupsPageContainer">
        <GroupsSection />
      </div>
    </AdminLayout>
  )
}
