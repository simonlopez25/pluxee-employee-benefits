import { useState } from 'react'
import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon/Icon'
// Reutilizamos los estilos del modal de beneficios para que se vean iguales
import '../BenefitFormModal/BenefitFormModal.css'
import './PackageFormModal.css'

export function PackageFormModal({
  departments,
  benefits,
  onClose,
  onSubmit,
  isSubmitting,
  apiError,
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [amount, setAmount] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [selectedBenefitIds, setSelectedBenefitIds] = useState([])
  const [validationError, setValidationError] = useState('')

  // Marca o desmarca un beneficio de la lista
  const toggleBenefit = (benefitId) => {
    if (selectedBenefitIds.includes(benefitId)) {
      setSelectedBenefitIds(selectedBenefitIds.filter((id) => id !== benefitId))
    } else {
      setSelectedBenefitIds([...selectedBenefitIds, benefitId])
    }
  }

  // 1 beneficio = MONO, 2 o más = MULTI (la misma regla que el backend)
  const packageTypeLabel =
    selectedBenefitIds.length === 1 ? 'Monobeneficio' : 'Multibeneficio'

  const handleSubmit = (event) => {
    event.preventDefault()
    const trimmedName = name.trim()

    // Validación temprana: avisamos antes de llamar al backend
    if (!trimmedName) {
      setValidationError('El nombre del paquete es obligatorio')
      return
    }
    if (trimmedName.length > 100) {
      setValidationError('El nombre no puede superar los 100 caracteres')
      return
    }
    if (amount === '' || Number(amount) < 0) {
      setValidationError('El importe debe ser un número mayor o igual que 0')
      return
    }
    if (!departmentId) {
      setValidationError('Elige un departamento')
      return
    }
    if (selectedBenefitIds.length === 0) {
      setValidationError('Elige al menos un beneficio')
      return
    }

    setValidationError('')
    // Mismos nombres de campo que espera PackageCreate en el backend
    onSubmit({
      name: trimmedName,
      description: description.trim() || null,
      default_amount: amount,
      department_id: Number(departmentId),
      benefit_ids: selectedBenefitIds,
    })
  }

  return (
    <div className="modalBackdrop" onClick={onClose}>
      <div
        className="modalContainer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="packageModalTitle"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modalHeader">
          <div className="modalHeaderInfo">
            <h2 id="packageModalTitle" className="modalTitle">
              Nuevo paquete
            </h2>
            <p className="modalSubtitle">
              Agrupa uno o varios beneficios con un importe por empleado.
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

        <form onSubmit={handleSubmit} className="modalForm" noValidate>
          <div className="modalBody">
            {(validationError || apiError) && (
              <div className="modalAlertConflict" role="alert">
                <span className="modalAlertText">{validationError || apiError}</span>
              </div>
            )}

            <div className="formField">
              <label htmlFor="packageName" className="formLabel">
                Nombre del paquete <span className="formRequiredMark">*</span>
              </label>
              <input
                id="packageName"
                type="text"
                maxLength={100}
                placeholder="Ej. Comida y transporte"
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="formInput"
                disabled={isSubmitting}
              />
            </div>

            <div className="formField">
              <label htmlFor="packageDescription" className="formLabel">
                Descripción
              </label>
              <textarea
                id="packageDescription"
                rows={2}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                className="formTextarea"
                disabled={isSubmitting}
              />
            </div>

            <div className="formField">
              <label htmlFor="packageAmount" className="formLabel">
                Importe por empleado (€) <span className="formRequiredMark">*</span>
              </label>
              <input
                id="packageAmount"
                type="number"
                min="0"
                step="0.01"
                placeholder="Ej. 100"
                value={amount}
                onChange={(event) => setAmount(event.target.value)}
                className="formInput"
                disabled={isSubmitting}
              />
            </div>

            <div className="formField">
              <label htmlFor="packageDepartment" className="formLabel">
                Departamento <span className="formRequiredMark">*</span>
              </label>
              <select
                id="packageDepartment"
                value={departmentId}
                onChange={(event) => setDepartmentId(event.target.value)}
                className="formInput"
                disabled={isSubmitting}
              >
                <option value="">Elige un departamento</option>
                {departments.map((department) => (
                  <option key={department.id} value={department.id}>
                    {department.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="formField">
              <span className="formLabel">
                Beneficios <span className="formRequiredMark">*</span>
                {selectedBenefitIds.length > 0 && (
                  <span className="packageTypeHint"> · {packageTypeLabel}</span>
                )}
              </span>
              <div className="formTogglesGroup">
                {benefits.map((benefit) => (
                  <label key={benefit.id} className="formCheckboxLabel">
                    <input
                      type="checkbox"
                      checked={selectedBenefitIds.includes(benefit.id)}
                      onChange={() => toggleBenefit(benefit.id)}
                      disabled={isSubmitting}
                      className="formCheckboxInput"
                    />
                    <span className="formCheckboxCustom" />
                    <span className="formCheckboxTitle">{benefit.name}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <footer className="modalFooter">
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button type="submit" variant="secondary" disabled={isSubmitting}>
              {isSubmitting ? 'Guardando...' : 'Crear paquete'}
            </Button>
          </footer>
        </form>
      </div>
    </div>
  )
}