import { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/templates/AdminLayout'
import { useAuth } from '../../context/AuthContext'
import { EmployeeFormModal } from '../../components/organisms/EmployeeFormModal'
import { DeactivateConfirmModal } from '../../components/organisms/DeactivateConfirmModal'
import {
  createUser,
  deactivateUser,
  getUsers,
  updateUser,
} from '../../services/userService'
import { getDepartments } from '../../services/departmentService'
import { EmployeesHeader } from './EmployeesHeader'
import { EmployeesAlerts } from './EmployeesAlerts'
import { EmployeesListHeader } from './EmployeesListHeader'
import { EmployeeTable } from './EmployeeTable'
import { EmployeeCardSkeleton } from './EmployeeCardSkeleton'
import { EmployeesEmptyState } from './EmployeesEmptyState'
import './EmployeesPage.css'

export function EmployeesPage() {
  const { user: currentUser } = useAuth()
  const [employees, setEmployees] = useState([])
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [modalMode, setModalMode] = useState('edit')
  const [editingEmployee, setEditingEmployee] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [modalApiError, setModalApiError] = useState(null)

  const [isDeactivateModalOpen, setIsDeactivateModalOpen] = useState(false)
  const [employeeToDeactivate, setEmployeeToDeactivate] = useState(null)
  const [isDeactivating, setIsDeactivating] = useState(false)

  useEffect(() => {
    let isCancelled = false
    const loadEmployees = async () => {
      try {
        const [usersData, departmentsData] = await Promise.all([
          getUsers(),
          getDepartments(),
        ])
        if (!isCancelled) {
          setEmployees(usersData)
          setDepartments(departmentsData)
          setErrorMessage(null)
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(
            error.message || 'Error al cargar la plantilla de empleados',
          )
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadEmployees()

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

  const handleOpenEditModal = (employee) => {
    setEditingEmployee(employee)
    setModalMode('edit')
    setModalApiError(null)
    setIsModalOpen(true)
  }

  const handleOpenCreateModal = () => {
    setEditingEmployee(null)
    setModalMode('create')
    setModalApiError(null)
    setIsModalOpen(true)
  }

  const handleOpenDeactivateModal = (employee) => {
    setEmployeeToDeactivate(employee)
    setIsDeactivateModalOpen(true)
  }

  const handleCloseModal = () => {
    if (!isSubmitting) {
      setIsModalOpen(false)
      setEditingEmployee(null)
      setModalApiError(null)
    }
  }

  const handleCloseDeactivateModal = () => {
    if (!isDeactivating) {
      setIsDeactivateModalOpen(false)
      setEmployeeToDeactivate(null)
    }
  }

  const handleCreateSubmit = async (formData) => {
    setIsSubmitting(true)
    setModalApiError(null)
    try {
      await createUser(formData)
      setSuccessMessage(
        'Empleado dado de alta. Deberá cambiar su contraseña al iniciar sesión',
      )
      setIsModalOpen(false)
      setEditingEmployee(null)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setModalApiError(
        error.status === 409
          ? 'Ya existe un empleado con ese correo electrónico'
          : error.message || 'Error al dar de alta al empleado',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEditSubmit = async (formData) => {
    setIsSubmitting(true)
    setModalApiError(null)
    try {
      await updateUser(editingEmployee.id, formData)
      setSuccessMessage('Empleado actualizado correctamente')
      setIsModalOpen(false)
      setEditingEmployee(null)
      setIsLoading(true)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setModalApiError(
        error.status === 409
          ? 'Ya existe un empleado con ese correo electrónico'
          : error.message || 'Error al actualizar el empleado',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeactivateConfirm = async () => {
    if (!employeeToDeactivate) {
      return
    }
    setIsDeactivating(true)
    try {
      await deactivateUser(employeeToDeactivate.id)
      setSuccessMessage('Empleado dado de baja correctamente')
      setIsDeactivateModalOpen(false)
      setEmployeeToDeactivate(null)
      setIsLoading(true)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setErrorMessage(error.message || 'Error al dar de baja al empleado')
    } finally {
      setIsDeactivating(false)
    }
  }

  const handleRetry = () => {
    setIsLoading(true)
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleDismissSuccess = () => setSuccessMessage(null)

  return (
    <AdminLayout>
      <section className="employeesPage">
        <EmployeesHeader onCreate={handleOpenCreateModal} />

        <EmployeesAlerts
          successMessage={successMessage}
          errorMessage={errorMessage}
          onDismissSuccess={handleDismissSuccess}
          onRetry={handleRetry}
        />

        <EmployeesListHeader count={employees.length} />

        {isLoading ? (
          <EmployeeCardSkeleton />
        ) : employees.length > 0 ? (
          <EmployeeTable
            employees={employees}
            departments={departments}
            currentUserId={currentUser?.id}
            isSubmitting={isSubmitting}
            isDeactivating={isDeactivating}
            onEdit={handleOpenEditModal}
            onDeactivate={handleOpenDeactivateModal}
          />
        ) : errorMessage ? null : (
          <EmployeesEmptyState onCreate={handleOpenCreateModal} />
        )}

        <EmployeeFormModal
          mode={modalMode}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSubmit={modalMode === 'create' ? handleCreateSubmit : handleEditSubmit}
          initialData={editingEmployee}
          isSubmitting={isSubmitting}
          apiError={modalApiError}
          departments={departments}
        />

        <DeactivateConfirmModal
          isOpen={isDeactivateModalOpen}
          onClose={handleCloseDeactivateModal}
          onConfirm={handleDeactivateConfirm}
          employee={employeeToDeactivate}
          isSubmitting={isDeactivating}
        />
      </section>
    </AdminLayout>
  )
}