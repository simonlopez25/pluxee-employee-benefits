// Middleware 404: cualquier ruta no matcheada llega aquí
export function notFound(req, res, next) {
  res.status(404).json({
    error: 'Not Found',
    message: `Ruta no encontrada: ${req.method} ${req.originalUrl}`,
  })
}

// Middleware de errores: captura excepciones de los controllers
// eslint-disable-next-line no-unused-vars
export function errorHandler(err, req, res, next) {
  console.error('[error]', err)
  res.status(err.status ?? 500).json({
    error: 'Internal Server Error',
    message: err.message ?? 'Error inesperado',
  })
}
