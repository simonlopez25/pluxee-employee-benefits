import { useEffect, useState } from 'react'
import { AdminLayout } from '../../components/templates/AdminLayout'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../../components/atoms/Button'
import { Icon } from '../../components/atoms/Icon'
import { Badge } from '../../components/atoms/Badge'
import { EmployeeFormModal } from '../../components/organisms/EmployeeFormModal'
import { DeactivateConfirmModal } from '../../components/organisms/DeactivateConfirmModal'
import {
  deactivateUser,
  getUsers,
  updateUser,
} from '../../services/userService'
import { getDepartments } from '../../services/departmentService'
import './EmployeesPage.css'

const formatDate = (value) => {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const STATUS_LABELS = {
  true: 'Activo',
  false: 'Inactivo',
}

export function EmployeesPage() {
  const { user: currentUser } = useAuth()
  const [employees, setEmployees] = useState([])
  const [departments, setDepartments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const [isModalOpen, setIsModalOpen] = useState(false)
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

  const isCurrentAdmin = (employeeId) => {
    return currentUser && currentUser.id === employeeId
  }

  const handleOpenEditModal = (employee) => {
    setEditingEmployee(employee)
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

  return (
    <AdminLayout>
      <section className="employeesPage">
        <header className="employeesHeader">
          <div className="employeesHeaderContent">
            <h1 className="employeesTitle">Empleados</h1>
            <p className="employeesSubtitle">
              Gestión de la plantilla: edición de datos y baja lógica de empleados.
            </p>
          </div>
        </header>

        {successMessage && (
          <div className="employeesAlertSuccess" role="status">
            <span className="employeesAlertIcon">
              <Icon name="check" size={16} />
            </span>
            <span className="employeesAlertText">{successMessage}</span>
            <button
              type="button"
              className="employeesAlertDismiss"
              onClick={() => setSuccessMessage(null)}
            >
              <Icon name="close" size={14} />
            </button>
          </div>
        )}

        {errorMessage && (
          <div className="employeesAlertError" role="alert">
            <span className="employeesAlertIcon">
              <Icon name="close" size={16} />
            </span>
            <span className="employeesAlertText">{errorMessage}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRetry}
              className="employeesRetryButton"
            >
              Reintentar
            </Button>
          </div>
        )}

        {!isLoading && employees.length > 0 && (
          <div className="employeesListHeader">
            <span className="employeesCountBadge">
              {employees.length}
              {employees.length === 1 ? 'empleado' : 'empleados'}
            </span>
          </div>
        )}

        {isLoading ? (
          <div className="employeesLoadingGrid">
            {[1, 2, 3].map((skeletonId) => (
              <div key={skeletonId} className="employeesCardSkeleton">
                <div className="employeesSkeletonRow" />
              </div>
            ))}
          </div>
        ) : employees.length > 0 ? (
          <div className="employeesTableWrapper">
            <table className="employeesTable">
              <thead>
                <tr>
                  <th className="employeesTableCell">Empleado</th>
                  <th className="employeesTableCell">Correo</th>
                  <th className="employeesTableCell">Rol</th>
                  <th className="employeesTableCell">Departamento</th>
                  <th className="employeesTableCell">Estado</th>
                  <th className="employeesTableCell">Fecha de baja</th>
                  <th className="employeesTableCell employeesTableActions">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                {employees.map((employee) => (
                  <tr key={employee.id} className="employeesTableRow">
                    <td className="employeesTableCell">
                      <span className="employeesTableName">
                        {employee.fullName}
                      </span>
                    </td>
                    <td className="employeesTableCell">{employee.email}</td>
                    <td className="employeesTableCell">
                      <Badge
                        variant={
                          employee.role === 'ADMIN' ? 'basic' : 'default'
                        }
                      >
                        {employee.role === 'ADMIN'
                          ? 'Administrador'
                          : 'Empleado'}
                      </Badge>
                    </td>
                    <td className="employeesTableCell">
                      {employee.departmentId ? (
                        <span>
                          {departments
                            .find((d) => d.id === employee.departmentId)
                            ?.name || '-'}
                        </span>
                      ) : (
                        <span className="employeesTableNone">—</span>
                      )}
                    </td>
                    <td className="employeesTableCell">
                      <Badge
                        variant={employee.isActive ? 'active' : 'inactive'}
                      >
                        {STATUS_LABELS[employee.isActive]}
                      </Badge>
                    </td>
                    <td className="employeesTableCell">
                      {employee.isActive ? (
                        <span className="employeesTableNone">—</span>
                      ) : (
                        <span>{formatDate(employee.deactivatedAt)}</span>
                      )}
                    </td>
                    <td className="employeesTableCell employeesTableActions">
                      <div className="employeesActionsGroup">
                        {employee.isActive && isCurrentAdmin(employee.id) && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleOpenEditModal(employee)}
                              disabled={isSubmitting || isDeactivating}
                              icon={<Icon name="edit" size={14} />}
                            >
                              Editar
                            </Button>
                            <span className="employeesActionsNote">
                              Tú (administrador)
                            </span>
                          </>
                        )}
                        {employee.isActive &&
                          !isCurrentAdmin(employee.id) && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleOpenEditModal(employee)}
                              disabled={isSubmitting || isDeactivating}
                              icon={<Icon name="edit" size={14} />}
                            >
                              Editar
                            </Button>
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() =>
                                handleOpenDeactivateModal(employee)
                              }
                              disabled={isSubmitting || isDeactivating}
                              icon={<Icon name="close" size={14} />}
                            >
                              Dar de baja
                            </Button>
                          </>
                        )}
                        {!employee.isActive && (
                          <span className="employeesActionsNone">
                            Inactivo
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : errorMessage ? null : (
          <div className="employeesEmptyState">
            <div className="employeesEmptyIconWrapper">
              <Icon name="groups" size={32} />
            </div>
            <h3 className="employeesEmptyTitle">
              No hay empleados registrados
            </h3>
            <p className="employeesEmptySubtitle">
              La plantilla está vacía. Los empleados se crean desde el backend.
            </p>
          </div>
        )}

        <EmployeeFormModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onSubmit={handleEditSubmit}
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
