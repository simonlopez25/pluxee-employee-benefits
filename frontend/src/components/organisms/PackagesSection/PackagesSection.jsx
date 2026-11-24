import { useEffect, useState } from 'react'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import { PackageFormModal } from '../PackageFormModal'
import { getBenefits } from '../../../services/benefitService'
import {
  createPackage,
  getActiveDepartments,
  getPackages,
} from '../../../services/packageService'
import { formatCurrency } from '../../../utils/format'
import './PackagesSection.css'

export function PackagesSection() {
  const [packages, setPackages] = useState([])
  const [departments, setDepartments] = useState([])
  const [benefits, setBenefits] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(null)

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [modalApiError, setModalApiError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)

  // Al montar el componente: pedimos paquetes, departamentos y beneficios a la vez
  useEffect(() => {
    const loadData = async () => {
      try {
        const [packagesData, departmentsData, benefitsData] = await Promise.all([
          getPackages(),
          getActiveDepartments(),
          getBenefits({ isActive: true }),
        ])
        setPackages(packagesData)
        setDepartments(departmentsData)
        setBenefits(benefitsData)
      } catch (error) {
        setErrorMessage(error.message)
      } finally {
        setIsLoading(false)
      }
    }
    loadData()
  }, [])

  // El paquete solo trae department_id: buscamos su nombre en la lista
  const getDepartmentName = (departmentId) => {
    const department = departments.find((item) => item.id === departmentId)
    return department ? department.name : `Departamento ${departmentId}`
  }

  const handleOpenModal = () => {
    setModalApiError(null)
    setSuccessMessage(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    if (!isSubmitting) {
      setIsModalOpen(false)
    }
  }

  // Envía el formulario al backend; si va bien, añade el paquete a la lista
  const handleCreatePackage = async (packageData) => {
    setIsSubmitting(true)
    setModalApiError(null)
    try {
      const newPackage = await createPackage(packageData)
      setPackages([...packages, newPackage])
      setSuccessMessage(`Paquete "${newPackage.name}" creado`)
      setIsModalOpen(false)
    } catch (error) {
      // Ej. 409: ya existe un paquete con ese nombre en este departamento
      setModalApiError(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="packagesSection">
      <div className="packagesHeader">
        <h2 className="packagesTitle">Paquetes</h2>
        <Button
          variant="secondary"
          onClick={handleOpenModal}
          disabled={isLoading || Boolean(errorMessage)}
          icon={<Icon name="plus" size={18} />}
        >
          Nuevo paquete
        </Button>
      </div>

      {successMessage && (
        <p className="packagesSuccess" role="status">
          {successMessage}
        </p>
      )}
      {isLoading && <p>Cargando paquetes...</p>}
      {errorMessage && <p role="alert">{errorMessage}</p>}
      {!isLoading && !errorMessage && packages.length === 0 && (
        <p>Todavía no hay paquetes creados.</p>
      )}

      <div className="packagesGrid">
        {packages.map((item) => (
          <div key={item.id} className="packageCard">
            <h3 className="packageCardTitle">{item.name}</h3>
            <p className="packageCardSubtitle">
              {getDepartmentName(item.department_id)} ·{' '}
              {item.package_type === 'MONO' ? 'Monobeneficio' : 'Multibeneficio'}
            </p>
            <div className="packageCardMeta">
              <span>{formatCurrency(item.default_amount)} por empleado</span>
              <span>{item.benefits.map((benefit) => benefit.name).join(' · ')}</span>
            </div>
          </div>
        ))}
      </div>

      {isModalOpen && (
        <PackageFormModal
          departments={departments}
          benefits={benefits}
          onClose={handleCloseModal}
          onSubmit={handleCreatePackage}
          isSubmitting={isSubmitting}
          apiError={modalApiError}
        />
      )}
    </section>
  )
}