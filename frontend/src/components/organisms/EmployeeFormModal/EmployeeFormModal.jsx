import { useEffect } from 'react'
import { EmployeeFormDialogContent } from './EmployeeFormDialogContent'

export function EmployeeFormModal({
  mode = 'edit',
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
  isSubmitting = false,
  apiError = null,
  departments = [],
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

  const formKey = `${mode}-${initialData?.id ?? 'new'}`

  return (
    <div className="employeeModalBackdrop" onClick={onClose}>
      <EmployeeFormDialogContent
        key={formKey}
        mode={mode}
        onClose={onClose}
        onSubmit={onSubmit}
        initialData={initialData}
        isSubmitting={isSubmitting}
        apiError={apiError}
        departments={departments}
      />
    </div>
  )
}