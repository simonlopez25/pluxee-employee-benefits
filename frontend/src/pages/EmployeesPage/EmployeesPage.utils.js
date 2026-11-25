export const STATUS_LABELS = {
  true: 'Activo',
  false: 'Inactivo',
}

export const formatDate = (value) => {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}