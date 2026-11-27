export const ROLE_OPTIONS = [
  { value: 'ADMIN', label: 'Administrador' },
  { value: 'EMPLOYEE', label: 'Empleado' },
]

export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
export const MIN_TEMPORARY_PASSWORD_LENGTH = 10

// Helper compartido: valida fullName y email (usado en create y edit)
function validateNameAndEmail(fullName, email) {
  const trimmedFullName = fullName.trim()
  const trimmedEmail = email.trim().toLowerCase()

  if (!trimmedFullName) {
    return { field: 'fullName', message: 'El nombre completo es obligatorio' }
  }
  if (trimmedFullName.length > 120) {
    return { field: 'fullName', message: 'El nombre no puede superar los 120 caracteres' }
  }
  if (!trimmedEmail) {
    return { field: 'email', message: 'El correo electrónico es obligatorio' }
  }
  if (!EMAIL_REGEX.test(trimmedEmail)) {
    return { field: 'email', message: 'El correo electrónico no tiene un formato válido' }
  }
  return null
}

export const validateCreateForm = ({
  fullName,
  email,
  temporaryPassword,
  departmentId,
}) => {
  const nameEmailError = validateNameAndEmail(fullName, email)
  if (nameEmailError) return nameEmailError

  if (!temporaryPassword || !temporaryPassword.trim()) {
    return { field: 'temporaryPassword', message: 'La contraseña temporal es obligatoria' }
  }
  if (temporaryPassword.trim().length < MIN_TEMPORARY_PASSWORD_LENGTH) {
    return {
      field: 'temporaryPassword',
      message: `La contraseña temporal debe tener al menos ${MIN_TEMPORARY_PASSWORD_LENGTH} caracteres`,
    }
  }
  if (!departmentId) {
    return { field: 'department', message: 'Debe seleccionar un departamento para el empleado' }
  }

  return null
}

export const validateEditForm = ({
  fullName,
  email,
  departmentId,
  departmentRequired,
}) => {
  const nameEmailError = validateNameAndEmail(fullName, email)
  if (nameEmailError) return nameEmailError

  if (departmentRequired && !departmentId) {
    return { field: 'department', message: 'Debe seleccionar un departamento para el empleado' }
  }
  if (!departmentRequired && departmentId) {
    return { field: 'department', message: 'Un administrador no puede tener departamento asignado' }
  }

  return null
}