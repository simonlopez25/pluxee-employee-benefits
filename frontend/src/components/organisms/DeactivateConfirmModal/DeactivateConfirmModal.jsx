import { useEffect } from 'react'
import { Button } from '../../atoms/Button'
import { Icon } from '../../atoms/Icon'
import './DeactivateConfirmModal.css'

function DeactivateConfirmDialogContent({
  onClose,
  onConfirm,
  employee,
  isSubmitting,
}) {
  const employeeName = employee?.fullName || 'este empleado'

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!employee) {
    return null
  }

  return (
    <div
      className="deactivateModalContainer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="deactivateModalTitle"
      onClick={(event) => event.stopPropagation()}
    >
      <header className="deactivateModalHeader">
        <div className="deactivateModalHeaderInfo">
          <h2 id="deactivateModalTitle" className="deactivateModalTitle">
            Dar de baja a {employeeName}
          </h2>
          <p className="deactivateModalSubtitle">
            Esta acción no se puede deshacer desde esta pantalla.
          </p>
        </div>
        <button
          type="button"
          className="deactivateModalCloseButton"
          onClick={onClose}
          disabled={isSubmitting}
          aria-label="Cerrar"
        >
          <Icon name="close" size={18} />
        </button>
      </header>

      <div className="deactivateModalBody">
        <div className="deactivateModalAlert" role="alert">
          <span className="deactivateModalAlertIcon">
            <Icon name="alert" size={18} />
          </span>
          <div className="deactivateModalAlertContent">
            <p className="deactivateModalAlertText">
              Al dar de baja a <strong>{employeeName}</strong>:
            </p>
            <ul className="deactivateModalAlertList">
              <li>
                Perderá el acceso a la plataforma de forma <strong>inmediata</strong>.
              </li>
              <li>
                Se registrará la <strong>fecha y hora de baja</strong> para trazabilidad.
              </li>
              <li>
                Sus gastos y asignaciones históricas <strong>seguirán visibles</strong>
                para auditoría (no se borra ningún registro).
              </li>
            </ul>
          </div>
        </div>
      </div>

      <footer className="deactivateModalFooter">
        <Button
          type="button"
          variant="outline"
          onClick={onClose}
          disabled={isSubmitting}
        >
          Cancelar
        </Button>
        <Button
          type="button"
          variant="danger"
          onClick={onConfirm}
          disabled={isSubmitting}
          icon={isSubmitting ? <Icon name="spinner" size={16} /> : null}
        >
          {isSubmitting ? 'Procesando...' : 'Dar de baja'}
        </Button>
      </footer>
    </div>
  )
}

export function DeactivateConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  employee,
  isSubmitting = false,
}) {
  if (!isOpen) {
    return null
  }

  return (
    <div className="deactivateModalBackdrop" onClick={onClose}>
      <DeactivateConfirmDialogContent
        onClose={onClose}
        onConfirm={onConfirm}
        employee={employee}
        isSubmitting={isSubmitting}
      />
    </div>
  )
}
