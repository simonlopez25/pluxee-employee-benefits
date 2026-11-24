import { getJson, postJson } from './http'

// GET /api/packages → lista de todos los paquetes
export function getPackages() {
  return getJson('/packages')
}

// POST /api/packages → crea un paquete y devuelve el paquete creado
export function createPackage(packageData) {
  return postJson('/packages', packageData)
}

// GET /api/departments?is_active=true → departamentos activos (para el formulario)
export function getActiveDepartments() {
  return getJson('/departments?is_active=true')
}