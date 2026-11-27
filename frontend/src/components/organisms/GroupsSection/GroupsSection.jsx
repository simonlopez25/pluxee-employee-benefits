import { useEffect, useState } from 'react'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon'
import { DepartmentCard } from '../../molecules/DepartmentCard'
import { DepartmentFormModal } from '../DepartmentFormModal'
import {
  createDepartment,
  getDepartments,
  updateDepartment,
} from '../../../services/departmentService'
import { getMonthlyBudgets } from '../../../services/budgetService'
import './GroupsSection.css'

const NAME_TAKEN_MESSAGE = 'Ya existe un grupo con ese nombre.'

const getCurrentMonthFirstDay = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}-01`
}

const mergeDepartmentsWithBudgets = (departmentsList, monthlyBudgetsData) => {
  const budgetItems = Array.isArray(monthlyBudgetsData?.departments)
    ? monthlyBudgetsData.departments
    : []

  const budgetByDepartmentId = new Map()
  for (const item of budgetItems) {
    const deptId = item.department_id ?? item.departmentId
    if (deptId !== undefined && deptId !== null) {
      budgetByDepartmentId.set(Number(deptId), item)
    }
  }

  return departmentsList.map((dept) => ({
    ...dept,
    monthlyBudget: budgetByDepartmentId.get(Number(dept.id)) ?? null,
  }))
}

export function GroupsSection() {
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDepartment, setEditingDepartment] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [modalApiError, setModalApiError] = useState(null)

  useEffect(() => {
    let isCancelled = false
    const loadDepartments = async () => {
      try {
        const data = await getDepartments()
        let monthlyBudgetsData = null

        try {
          monthlyBudgetsData = await getMonthlyBudgets(getCurrentMonthFirstDay())
        } catch {
          monthlyBudgetsData = null
        }

        if (!isCancelled) {
          setDepartments(mergeDepartmentsWithBudgets(data, monthlyBudgetsData))
          setErrorMessage(null)
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(error.message || 'Error al cargar los grupos')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadDepartments()

    return () => {
      isCancelled = true
    }
  }, [refreshTrigger])

  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null)
      }, 4000)
      return () => clearTimeout(timer)
    }
  }, [successMessage])

  const handleOpenCreateModal = () => {
    setEditingDepartment(null)
    setModalApiError(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (department) => {
    setEditingDepartment(department)
    setModalApiError(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    if (!isSubmitting) {
      setIsModalOpen(false)
      setEditingDepartment(null)
      setModalApiError(null)
    }
  }

  const handleModalSubmit = async (formData) => {
    setIsSubmitting(true)
    setModalApiError(null)
    try {
      if (editingDepartment) {
        await updateDepartment(editingDepartment.id, formData)
        setSuccessMessage('Grupo actualizado correctamente')
      } else {
        await createDepartment(formData)
        setSuccessMessage('Grupo creado con éxito')
      }
      setIsModalOpen(false)
      setEditingDepartment(null)
      setIsLoading(true)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setModalApiError(
        error.status === 409
          ? NAME_TAKEN_MESSAGE
          : error.message || 'Error al guardar el grupo',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRetry = () => {
    setIsLoading(true)
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <section className="groupsSection">
      <header className="groupsHeader">
        <div className="groupsHeaderContent">
          <h1 className="groupsTitle">Grupos</h1>
          <p className="groupsSubtitle">
            Organiza a la plantilla por equipos para asignar paquetes y presupuestos.
          </p>
        </div>

        <div className="groupsHeaderActions">
          <Button
            variant="secondary"
            size="md"
            onClick={handleOpenCreateModal}
            icon={<Icon name="plus" size={18} />}
          >
            Nuevo grupo
          </Button>
        </div>
      </header>

      {successMessage && (
        <div className="groupsAlertSuccess" role="status">
          <span className="groupsAlertIcon">
            <Icon name="check" size={16} />
          </span>
          <span className="groupsAlertText">{successMessage}</span>
          <button
            type="button"
            className="groupsAlertDismiss"
            onClick={() => setSuccessMessage(null)}
          >
            <Icon name="close" size={14} />
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="groupsAlertError" role="alert">
          <span className="groupsAlertIcon">
            <Icon name="close" size={16} />
          </span>
          <span className="groupsAlertText">{errorMessage}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRetry}
            className="groupsRetryButton"
          >
            Reintentar
          </Button>
        </div>
      )}

      {!isLoading && departments.length > 0 && (
        <div className="groupsListHeader">
          <span className="groupsCountBadge">
            {departments.length} {departments.length === 1 ? 'grupo' : 'grupos'}
          </span>
        </div>
      )}

      {isLoading ? (
        <div className="groupsLoadingGrid">
          {[1, 2, 3].map((skeletonId) => (
            <div key={skeletonId} className="groupsCardSkeleton">
              <div className="groupsSkeletonHeader">
                <div className="groupsSkeletonTitle" />
                <div className="groupsSkeletonBadge" />
              </div>
            </div>
          ))}
        </div>
      ) : departments.length > 0 ? (
        <div className="groupsGrid">
          {departments.map((department) => (
            <DepartmentCard
              key={department.id}
              department={department}
              onEdit={handleOpenEditModal}
            />
          ))}
        </div>
      ) : errorMessage ? null : (
        <div className="groupsEmptyState">
          <div className="groupsEmptyIconWrapper">
            <Icon name="groups" size={32} />
          </div>
          <h3 className="groupsEmptyTitle">No hay grupos registrados</h3>
          <p className="groupsEmptySubtitle">
            Empieza creando el primer grupo para estructurar la plantilla.
          </p>
          <Button
            variant="secondary"
            size="md"
            onClick={handleOpenCreateModal}
            icon={<Icon name="plus" size={16} />}
          >
            Nuevo grupo
          </Button>
        </div>
      )}

      <DepartmentFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleModalSubmit}
        initialData={editingDepartment}
        isSubmitting={isSubmitting}
        apiError={modalApiError}
      />
    </section>
  )
}