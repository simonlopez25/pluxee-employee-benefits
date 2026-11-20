import { useEffect, useState } from 'react'
import { Button } from '../atoms/Button'
import { Icon } from '../atoms/Icon'
import './BenefitFormModal.css'

function BenefitFormDialogContent({
  onClose,
  onSubmit,
  initialData,
  isSubmitting,
  apiError,
}) {
  const [name, setName] = useState(initialData?.name || '')
  const [description, setDescription] = useState(initialData?.description || '')
  const [isBasic, setIsBasic] = useState(Boolean(initialData?.isBasic))
  const [isActive, setIsActive] = useState(
    initialData?.isActive !== undefined ? Boolean(initialData.isActive) : true
  )
  const [validationError, setValidationError] = useState('')

  const isEditMode = Boolean(initialData && initialData.id)

  const handleSubmit = (event) => {
    event.preventDefault()
    const trimmedName = name.trim()

    if (!trimmedName) {
      setValidationError('El nombre del beneficio es obligatorio')
      return
    }

    if (trimmedName.length > 80) {
      setValidationError('El nombre no puede superar los 80 caracteres')
      return
    }

    setValidationError('')
    onSubmit({
      name: trimmedName,
      description: description.trim(),
      isBasic,
      isActive,
    })
  }

  return (
    <div
      className="modalContainer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modalTitle"
      onClick={(event) => event.stopPropagation()}
    >
      <header className="modalHeader">
        <div className="modalHeaderInfo">
          <h2 id="modalTitle" className="modalTitle">
            {isEditMode ? 'Editar beneficio' : 'Nuevo beneficio'}
          </h2>
          <p className="modalSubtitle">
            {isEditMode
              ? 'Modifica los datos del beneficio existente.'
              : 'Define una nueva categoría para los paquetes de empleados.'}
          </p>
        </div>
        <button
          type="button"
          className="modalCloseButton"
          onClick={onClose}
          disabled={isSubmitting}
          aria-label="Cerrar modal"
        >
          <Icon name="close" size={18} />
        </button>
      </header>

      <form onSubmit={handleSubmit} className="modalForm">
        <div className="modalBody">
          {apiError && (
            <div className="modalAlertConflict" role="alert">
              <span className="modalAlertIcon">
                <Icon name="close" size={16} />
              </span>
              <span className="modalAlertText">{apiError}</span>
            </div>
          )}

          <div className="formField">
            <label htmlFor="benefitName" className="formLabel">
              Nombre del beneficio <span className="formRequiredMark">*</span>
            </label>
            <input
              id="benefitName"
              type="text"
              maxLength={80}
              placeholder="Ej. Comida, Transporte, Guardería..."
              value={name}
              onChange={(event) => {
                setName(event.target.value)
                if (validationError) {
                  setValidationError('')
                }
              }}
              className={`formInput ${validationError ? 'formInputError' : ''}`}
              disabled={isSubmitting}
              autoFocus
            />
            {validationError && (
              <span className="formErrorMessage">{validationError}</span>
            )}
          </div>

          <div className="formField">
            <label htmlFor="benefitDescription" className="formLabel">
              Descripción
            </label>
            <textarea
              id="benefitDescription"
              rows={3}
              placeholder="Indica las condiciones, límites o detalles del beneficio..."
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className="formTextarea"
              disabled={isSubmitting}
            />
          </div>

          <div className="formTogglesGroup">
            <label className="formCheckboxLabel">
              <input
                type="checkbox"
                checked={isBasic}
                onChange={(event) => setIsBasic(event.target.checked)}
                disabled={isSubmitting}
                className="formCheckboxInput"
              />
              <span className="formCheckboxCustom" />
              <span className="formCheckboxTextGroup">
                <span className="formCheckboxTitle">Beneficio básico</span>
                <span className="formCheckboxDescription">
                  Marca si este beneficio es parte del paquete base o esencial.
                </span>
              </span>
            </label>

            <label className="formCheckboxLabel">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(event) => setIsActive(event.target.checked)}
                disabled={isSubmitting}
                className="formCheckboxInput"
              />
              <span className="formCheckboxCustom" />
              <span className="formCheckboxTextGroup">
                <span className="formCheckboxTitle">Estado activo</span>
                <span className="formCheckboxDescription">
                  Disponible para ser asignado en nuevos paquetes de empleados.
                </span>
              </span>
            </label>
          </div>
        </div>

        <footer className="modalFooter">
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
                : 'Crear beneficio'}
          </Button>
        </footer>
      </form>
    </div>
  )
}

export function BenefitFormModal({
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
    <div className="modalBackdrop" onClick={onClose}>
      <BenefitFormDialogContent
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
