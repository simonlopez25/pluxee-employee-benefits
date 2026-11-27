import { useEffect, useState } from 'react'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon'
import './DepartmentFormModal.css'

const CURRENCY_OPTIONS = ['EUR', 'USD', 'GBP']

function DepartmentFormDialogContent({
  onClose,
  onSubmit,
  initialData,
  isSubmitting,
  apiError,
}) {
  const [name, setName] = useState(initialData?.name || '')
  const [currency, setCurrency] = useState(initialData?.currency || 'EUR')
  const [validationError, setValidationError] = useState('')

  const isEditMode = Boolean(initialData && initialData.id)

  const handleSubmit = (event) => {
    event.preventDefault()
    const trimmedName = name.trim()

    if (!trimmedName) {
      setValidationError('El nombre del grupo es obligatorio')
      return
    }

    if (trimmedName.length > 100) {
      setValidationError('El nombre no puede superar los 100 caracteres')
      return
    }

    setValidationError('')
    onSubmit({ name: trimmedName, currency })
  }

  return (
    <div
      className="departmentModalContainer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="departmentModalTitle"
      onClick={(event) => event.stopPropagation()}
    >
      <header className="departmentModalHeader">
        <div className="departmentModalHeaderInfo">
          <h2 id="departmentModalTitle" className="departmentModalTitle">
            {isEditMode ? 'Editar grupo' : 'Nuevo grupo'}
          </h2>
          <p className="departmentModalSubtitle">
            {isEditMode
              ? 'Modifica el nombre o la divisa de este grupo.'
              : 'Crea un grupo para estructurar la plantilla y sus presupuestos.'}
          </p>
        </div>
        <button
          type="button"
          className="departmentModalCloseButton"
          onClick={onClose}
          disabled={isSubmitting}
          aria-label="Cerrar modal"
        >
          <Icon name="close" size={18} />
        </button>
      </header>

      <form onSubmit={handleSubmit} className="departmentModalForm">
        <div className="departmentModalBody">
          {apiError && (
            <div className="departmentModalAlert" role="alert">
              <span className="departmentModalAlertIcon">
                <Icon name="close" size={16} />
              </span>
              <span className="departmentModalAlertText">{apiError}</span>
            </div>
          )}

          <div className="departmentModalField">
            <label htmlFor="departmentName" className="departmentModalLabel">
              Nombre del grupo <span className="departmentModalRequiredMark">*</span>
            </label>
            <input
              id="departmentName"
              type="text"
              maxLength={100}
              placeholder="Ej. Marketing, Producto, Operaciones..."
              value={name}
              onChange={(event) => {
                setName(event.target.value)
                if (validationError) {
                  setValidationError('')
                }
              }}
              className={`departmentModalInput ${validationError ? 'departmentModalInputError' : ''}`}
              disabled={isSubmitting}
              autoFocus
            />
            {validationError && (
              <span className="departmentModalErrorMessage">{validationError}</span>
            )}
          </div>

          <div className="departmentModalField">
            <label htmlFor="departmentCurrency" className="departmentModalLabel">
              Divisa
            </label>
            <select
              id="departmentCurrency"
              value={currency}
              onChange={(event) => setCurrency(event.target.value)}
              className="departmentModalInput"
              disabled={isSubmitting}
            >
              {CURRENCY_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        </div>

        <footer className="departmentModalFooter">
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
            {isSubmitting
              ? 'Guardando...'
              : isEditMode
                ? 'Guardar cambios'
                : 'Crear grupo'}
          </Button>
        </footer>
      </form>
    </div>
  )
}

export function DepartmentFormModal({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
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

  const formKey = initialData?.id ? `edit-${initialData.id}` : 'create-new'

  return (
    <div className="departmentModalBackdrop" onClick={onClose}>
      <DepartmentFormDialogContent
        key={formKey}
        onClose={onClose}
        onSubmit={onSubmit}
        initialData={initialData}
        isSubmitting={isSubmitting}
        apiError={apiError}
      />
    </div>
  )
}