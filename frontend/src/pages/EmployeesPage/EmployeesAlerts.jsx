import { Button } from '../../components/atoms/Button'
import { Icon } from '../../components/atoms/Icon'

export function EmployeesAlerts({
  successMessage,
  errorMessage,
  onDismissSuccess,
  onRetry,
}) {
  return (
    <>
      {successMessage && (
        <div className="employeesAlertSuccess" role="status">
          <span className="employeesAlertIcon">
            <Icon name="check" size={16} />
          </span>
          <span className="employeesAlertText">{successMessage}</span>
          <button
            type="button"
            className="employeesAlertDismiss"
            onClick={onDismissSuccess}
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
            onClick={onRetry}
            className="employeesRetryButton"
          >
            Reintentar
          </Button>
        </div>
      )}
    </>
  )
}