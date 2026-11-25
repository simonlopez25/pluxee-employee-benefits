import { getJson, postJson, putJson } from './http'

const mapDepartmentFromApi = (item) => ({
  id: item.id,
  name: item.name,
  currency: item.currency,
  isActive: Boolean(item.is_active),
  createdAt: item.created_at,
  employeeCount: Number(item.employee_count ?? item.employeeCount ?? 0) || 0,
  packages: Array.isArray(item.packages)
    ? item.packages.map((pkg) => ({ id: pkg.id, name: pkg.name }))
    : [],
})

const mapDepartmentToApi = (departmentData) => ({
  name: departmentData.name.trim(),
  currency: departmentData.currency.trim().toUpperCase(),
})

export const getDepartments = async (filters = {}) => {
  const params = new URLSearchParams()
  if (filters.isActive !== undefined && filters.isActive !== null) {
    params.set('is_active', String(filters.isActive))
  }
  const query = params.toString()
  const data = await getJson(`/departments${query ? `?${query}` : ''}`)
  return Array.isArray(data) ? data.map(mapDepartmentFromApi) : []
}

export const getDepartmentById = async (departmentId) => {
  const data = await getJson(`/departments/${departmentId}`)
  return mapDepartmentFromApi(data)
}

export const createDepartment = async (departmentData) => {
  const data = await postJson('/departments', mapDepartmentToApi(departmentData))
  return mapDepartmentFromApi(data)
}

export const updateDepartment = async (departmentId, departmentData) => {
  const data = await putJson(`/departments/${departmentId}`, mapDepartmentToApi(departmentData))
  return mapDepartmentFromApi(data)
}