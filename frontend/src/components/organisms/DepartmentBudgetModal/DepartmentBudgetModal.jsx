import { useEffect, useState } from 'react'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon'
import { formatCurrency } from '../../../utils/format'
import './DepartmentBudgetModal.css'

function DepartmentBudgetFormContent({
  department,
  availableCeiling,
  activeBenefits = [],
  onClose,
  onSubmit,
  isSubmitting,
  apiError,
}) {
  const [allocatedAmount, setAllocatedAmount] = useState(
    department?.allocatedAmount > 0 ? String(department.allocatedAmount) : ''
  )

  const [references, setReferences] = useState(() => {
    const existingMap = new Map()
    if (Array.isArray(department?.benefitReferences)) {
      department.benefitReferences.forEach((ref) => {
        existingMap.set(ref.benefitId, ref.indicativeAmount)
      })
    }
    return activeBenefits.map((benefit) => ({
      benefitId: benefit.id,
      benefitName: benefit.name,
      indicativeAmount: existingMap.has(benefit.id)
        ? String(existingMap.get(benefit.id))
        : '',
    }))
  })

  const [validationError, setValidationError] = useState('')

  const handleReferenceChange = (benefitId, value) => {
    setReferences((prev) =>
      prev.map((item) =>
        item.benefitId === benefitId ? { ...item, indicativeAmount: value } : item
      )
    )
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    const numericAllocated = parseFloat(allocatedAmount)

    if (isNaN(numericAllocated) || numericAllocated < 0) {
      setValidationError('Introduce un importe asignado válido mayor o igual a 0')
      return
    }

    if (numericAllocated > availableCeiling) {
      setValidationError(
        `El importe supera el saldo global disponible (${availableCeiling.toLocaleString(
          'es-ES',
          { style: 'currency', currency: 'EUR' }
        )})`
      )
      return
    }

    const cleanedReferences = references.map((item) => ({
      benefitId: item.benefitId,
      indicativeAmount: item.indicativeAmount
        ? Math.max(parseFloat(item.indicativeAmount) || 0, 0)
        : 0,
    }))

    setValidationError('')
    onSubmit({
      allocatedAmount: numericAllocated,
      references: cleanedReferences,
    })
  }

  return (
    <div
      className="deptModalContainer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="deptModalTitle"
      onClick={(e) => e.stopPropagation()}
    >
      <header className="deptModalHeader">
        <div className="deptModalHeaderInfo">
          <h2 id="deptModalTitle" className="deptModalTitle">
            Presupuesto: {department?.departmentName}
          </h2>
          <p className="deptModalSubtitle">
            Asigna el presupuesto del departamento y sus referencias orientativas.
          </p>
        </div>
        <button
          type="button"
          className="deptModalCloseButton"
          onClick={onClose}
          disabled={isSubmitting}
          aria-label="Cerrar modal"
        >
          <Icon name="close" size={18} />
        </button>
      </header>

      <form onSubmit={handleSubmit} className="deptModalForm">
        <div className="deptModalBody">
          {apiError && (
            <div className="deptModalAlertError" role="alert">
              <Icon name="close" size={16} />
              <span>{apiError}</span>
            </div>
          )}

          <div className="deptModalField">
            <label htmlFor="deptAmountInput" className="deptModalLabel">
              Presupuesto asignado al departamento (€){' '}
              <span className="deptModalRequired">*</span>
            </label>
            <input
              id="deptAmountInput"
              type="number"
              step="0.01"
              min="0"
              placeholder="Ej. 2500.00"
              value={allocatedAmount}
              onChange={(e) => {
                setAllocatedAmount(e.target.value)
                if (validationError) {
                  setValidationError('')
                }
              }}
              className={`deptModalInput ${
                validationError ? 'deptModalInputError' : ''
              }`}
              disabled={isSubmitting}
              autoFocus
            />
            {validationError ? (
              <span className="deptModalErrorMessage">{validationError}</span>
            ) : (
              <span className="deptModalHint">
                Máximo disponible para repartir:{' '}
                <strong>
                  {formatCurrency(availableCeiling)}
                </strong>
              </span>
            )}
          </div>

          <div className="deptModalSectionDivider" />

          <div className="deptModalReferencesSection">
            <h3 className="deptModalSectionTitle">
              Referencias orientativas por beneficio
            </h3>

            <div className="deptModalNoticeBanner">
              <Icon name="info" size={18} className="deptModalNoticeIcon" />
              <p className="deptModalNoticeText">
                Estos importes por beneficio son solo una referencia orientativa para
                planificación; no suman ni bloquean el presupuesto del grupo ni los
                gastos de los empleados.
              </p>
            </div>

            <div className="deptModalReferencesGrid">
              {references.map((item) => (
                <div key={item.benefitId} className="deptReferenceField">
                  <label
                    htmlFor={`ref-${item.benefitId}`}
                    className="deptReferenceLabel"
                  >
                    {item.benefitName}
                  </label>
                  <input
                    id={`ref-${item.benefitId}`}
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00 €"
                    value={item.indicativeAmount}
                    onChange={(e) =>
                      handleReferenceChange(item.benefitId, e.target.value)
                    }
                    className="deptReferenceInput"
                    disabled={isSubmitting}
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <footer className="deptModalFooter">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="secondary"
            disabled={isSubmitting}
            icon={isSubmitting ? <Icon name="spinner" size={16} /> : null}
          >
            {isSubmitting ? 'Guardando...' : 'Guardar asignación'}
          </Button>
        </footer>
      </form>
    </div>
  )
}

export function DepartmentBudgetModal({
  isOpen,
  department,
  availableCeiling = 0,
  activeBenefits = [],
  onClose,
  onSubmit,
  isSubmitting = false,
  apiError = null,
}) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isOpen && !isSubmitting) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, isSubmitting, onClose])

  if (!isOpen) {
    return null
  }

  const formKey = `dept-${department?.departmentId}-${department?.allocatedAmount}`

  return (
    <div className="deptModalBackdrop" onClick={onClose}>
      <DepartmentBudgetFormContent
        key={formKey}
        department={department}
        availableCeiling={availableCeiling}
        activeBenefits={activeBenefits}
        onClose={onClose}
        onSubmit={onSubmit}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  )
}
