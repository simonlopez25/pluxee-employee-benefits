import { useEffect, useState } from 'react'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon/Icon'
import { formatCurrency } from '../../../utils/format'
import { MONTH_NAMES } from '../../../utils/dates'
import './GlobalBudgetModal.css'

function GlobalBudgetFormContent({
  period,
  currentTotal,
  allocatedFloor = 0,
  onClose,
  onSubmit,
  isSubmitting,
  apiError,
}) {
  const [totalAmount, setTotalAmount] = useState(
    currentTotal > 0 ? String(currentTotal) : ''
  )
  const [validationError, setValidationError] = useState('')

  const currentDate = new Date(period)
  const periodLabel = `${MONTH_NAMES[currentDate.getMonth()]} de ${currentDate.getFullYear()}`

  const handleSubmit = (event) => {
    event.preventDefault()
    const numeric = parseFloat(totalAmount)

    if (isNaN(numeric) || numeric < 0) {
      setValidationError('Introduce un importe válido mayor o igual a 0')
      return
    }

    if (numeric < allocatedFloor) {
      setValidationError(
        `El presupuesto global no puede ser inferior a lo ya repartido (${allocatedFloor.toLocaleString(
          'es-ES',
          { style: 'currency', currency: 'EUR' }
        )})`
      )
      return
    }

    setValidationError('')
    onSubmit(numeric)
  }

  return (
    <div
      className="globalModalContainer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="globalModalTitle"
      onClick={(e) => e.stopPropagation()}
    >
      <header className="globalModalHeader">
        <div className="globalModalHeaderInfo">
          <h2 id="globalModalTitle" className="globalModalTitle">
            Configurar presupuesto global
          </h2>
          <p className="globalModalSubtitle">
            Establece el techo financiero para {periodLabel}.
          </p>
        </div>
        <button
          type="button"
          className="globalModalCloseButton"
          onClick={onClose}
          disabled={isSubmitting}
          aria-label="Cerrar modal"
        >
          <Icon name="close" size={18} />
        </button>
      </header>

      <form onSubmit={handleSubmit} className="globalModalForm">
        <div className="globalModalBody">
          {apiError && (
            <div className="globalModalAlertError" role="alert">
              <Icon name="close" size={16} />
              <span>{apiError}</span>
            </div>
          )}

          <div className="globalModalFloorNotice">
            <Icon name="info" size={16} className="globalModalFloorIcon" />
            <div className="globalModalFloorText">
              <span>Suelo mínimo asignado: </span>
              <strong>
                {formatCurrency(allocatedFloor)}
              </strong>
              <p className="globalModalFloorHint">
                Ya ha sido asignado a departamentos. El global no puede ser inferior.
              </p>
            </div>
          </div>

          <div className="globalFormField">
            <label htmlFor="globalAmountInput" className="globalFormLabel">
              Importe total del mes (€) <span className="globalFormRequired">*</span>
            </label>
            <input
              id="globalAmountInput"
              type="number"
              step="0.01"
              min="0"
              placeholder="Ej. 10000.00"
              value={totalAmount}
              onChange={(e) => {
                setTotalAmount(e.target.value)
                if (validationError) {
                  setValidationError('')
                }
              }}
              className={`globalFormInput ${
                validationError ? 'globalFormInputError' : ''
              }`}
              disabled={isSubmitting}
              autoFocus
            />
            {validationError && (
              <span className="globalFormErrorMessage">{validationError}</span>
            )}
          </div>
        </div>

        <footer className="globalModalFooter">
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
            {isSubmitting ? 'Guardando...' : 'Guardar presupuesto'}
          </Button>
        </footer>
      </form>
    </div>
  )
}

export function GlobalBudgetModal({
  isOpen,
  period,
  currentTotal = 0,
  allocatedFloor = 0,
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

  const formKey = `global-${period}-${currentTotal}`

  return (
    <div className="globalModalBackdrop" onClick={onClose}>
      <GlobalBudgetFormContent
        key={formKey}
        period={period}
        currentTotal={currentTotal}
        allocatedFloor={allocatedFloor}
        onClose={onClose}
        onSubmit={onSubmit}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  )
}
