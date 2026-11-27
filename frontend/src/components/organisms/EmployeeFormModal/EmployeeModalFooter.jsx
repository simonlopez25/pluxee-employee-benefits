import { Button } from '../../atoms/Button/Button'
import { Icon } from '../../atoms/Icon/Icon'

export function EmployeeModalFooter({
  isCreate,
  isSubmitting,
  onClose,
}) {
  return (
    <footer className="employeeModalFooter">
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
          ? isCreate
            ? 'Creando...'
            : 'Guardando...'
          : isCreate
            ? 'Dar de alta'
            : 'Guardar cambios'}
      </Button>
    </footer>
  )
}