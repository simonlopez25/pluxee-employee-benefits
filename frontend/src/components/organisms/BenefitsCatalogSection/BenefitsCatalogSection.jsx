import { useEffect, useMemo, useState } from 'react'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon/Icon'
import { BenefitCard } from '../../molecules/BenefitCard'
import { FilterTabs } from '../../molecules/FilterTabs'
import { BenefitFormModal } from '../BenefitFormModal'
import {
  createBenefit,
  getBenefits,
  toggleBenefitStatus,
  updateBenefit,
} from '../../../services/benefitService'
import './BenefitsCatalogSection.css'

export function BenefitsCatalogSection() {
  const [benefits, setBenefits] = useState([])
  const [activeFilter, setActiveFilter] = useState('all')
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingBenefit, setEditingBenefit] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [modalApiError, setModalApiError] = useState(null)
  const [togglingBenefitId, setTogglingBenefitId] = useState(null)

  useEffect(() => {
    let isCancelled = false
    const loadBenefits = async () => {
      try {
        const data = await getBenefits()
        if (!isCancelled) {
          setBenefits(data)
          setErrorMessage(null)
        }
      } catch (error) {
        if (!isCancelled) {
          setErrorMessage(error.message || 'Error al cargar el catálogo de beneficios')
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    loadBenefits()

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

  const counts = useMemo(() => {
    return {
      all: benefits.length,
      active: benefits.filter((item) => item.isActive).length,
      inactive: benefits.filter((item) => !item.isActive).length,
      basic: benefits.filter((item) => item.isBasic).length,
    }
  }, [benefits])

  const filteredBenefits = useMemo(() => {
    switch (activeFilter) {
      case 'active':
        return benefits.filter((item) => item.isActive)
      case 'inactive':
        return benefits.filter((item) => !item.isActive)
      case 'basic':
        return benefits.filter((item) => item.isBasic)
      default:
        return benefits
    }
  }, [benefits, activeFilter])

  const handleOpenCreateModal = () => {
    setEditingBenefit(null)
    setModalApiError(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (benefit) => {
    setEditingBenefit(benefit)
    setModalApiError(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    if (!isSubmitting) {
      setIsModalOpen(false)
      setEditingBenefit(null)
      setModalApiError(null)
    }
  }

  const handleModalSubmit = async (formData) => {
    setIsSubmitting(true)
    setModalApiError(null)
    try {
      if (editingBenefit) {
        await updateBenefit(editingBenefit.id, formData)
        setSuccessMessage('Beneficio actualizado correctamente')
      } else {
        await createBenefit(formData)
        setSuccessMessage('Beneficio creado con éxito')
      }
      setIsModalOpen(false)
      setEditingBenefit(null)
      setIsLoading(true)
      setRefreshTrigger((prev) => prev + 1)
    } catch (error) {
      setModalApiError(error.message || 'Error al guardar el beneficio')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleToggleStatus = async (benefitId, targetStatus) => {
    setTogglingBenefitId(benefitId)
    try {
      await toggleBenefitStatus(benefitId, { isActive: targetStatus })
      setBenefits((prev) =>
        prev.map((item) =>
          item.id === benefitId ? { ...item, isActive: targetStatus } : item
        )
      )
      setSuccessMessage(
        targetStatus
          ? 'Beneficio activado correctamente'
          : 'Beneficio desactivado correctamente'
      )
    } catch (error) {
      setErrorMessage(error.message || 'Error al cambiar el estado del beneficio')
    } finally {
      setTogglingBenefitId(null)
    }
  }

  const handleRetry = () => {
    setIsLoading(true)
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <section className="catalogSection">
      <header className="catalogHeader">
        <div className="catalogHeaderContent">
          <h1 className="catalogTitle">Catálogo de beneficios</h1>
          <p className="catalogSubtitle">
            Beneficios disponibles y paquetes que puedes asignar.
          </p>
        </div>

        <div className="catalogHeaderActions">
          <Button
            variant="secondary"
            size="md"
            onClick={handleOpenCreateModal}
            icon={<Icon name="plus" size={18} />}
          >
            Nuevo beneficio
          </Button>
        </div>
      </header>

      {successMessage && (
        <div className="catalogAlertSuccess" role="status">
          <span className="catalogAlertIcon">
            <Icon name="check" size={16} />
          </span>
          <span className="catalogAlertText">{successMessage}</span>
          <button
            type="button"
            className="catalogAlertDismiss"
            onClick={() => setSuccessMessage(null)}
          >
            <Icon name="close" size={14} />
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="catalogAlertError" role="alert">
          <span className="catalogAlertIcon">
            <Icon name="close" size={16} />
          </span>
          <span className="catalogAlertText">{errorMessage}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRetry}
            className="catalogRetryButton"
          >
            Reintentar
          </Button>
        </div>
      )}

      <div className="catalogSubheader">
        <h2 className="catalogSectionLabel">Beneficios</h2>
        <div className="catalogFiltersWrapper">
          <FilterTabs
            activeFilter={activeFilter}
            onFilterChange={setActiveFilter}
            counts={counts}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="catalogLoadingGrid">
          {[1, 2, 3, 4, 5].map((skeletonId) => (
            <div key={skeletonId} className="catalogCardSkeleton">
              <div className="skeletonHeader">
                <div className="skeletonIcon" />
                <div className="skeletonBadge" />
              </div>
              <div className="skeletonTitle" />
              <div className="skeletonText" />
              <div className="skeletonFooter" />
            </div>
          ))}
        </div>
      ) : filteredBenefits.length === 0 ? (
        <div className="catalogEmptyState">
          <div className="catalogEmptyIconWrapper">
            <Icon name="catalog" size={32} />
          </div>
          <h3 className="catalogEmptyTitle">No hay beneficios registrados</h3>
          <p className="catalogEmptySubtitle">
            {activeFilter !== 'all'
              ? 'No se encontraron beneficios con el filtro seleccionado.'
              : 'Empieza creando el primer beneficio del catálogo para los paquetes de tu empresa.'}
          </p>
          {activeFilter !== 'all' ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveFilter('all')}
            >
              Ver todos los beneficios
            </Button>
          ) : (
            <Button
              variant="secondary"
              size="md"
              onClick={handleOpenCreateModal}
              icon={<Icon name="plus" size={16} />}
            >
              Nuevo beneficio
            </Button>
          )}
        </div>
      ) : (
        <div className="catalogGrid">
          {filteredBenefits.map((benefit) => (
            <BenefitCard
              key={benefit.id}
              benefit={benefit}
              onEdit={handleOpenEditModal}
              onToggleStatus={handleToggleStatus}
              isToggling={togglingBenefitId === benefit.id}
            />
          ))}
        </div>
      )}

      <BenefitFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleModalSubmit}
        initialData={editingBenefit}
        isSubmitting={isSubmitting}
        apiError={modalApiError}
      />
    </section>
  )
}

