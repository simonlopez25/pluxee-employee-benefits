import { patchJson, request } from './http'

const mapUserFromApi = (item) => ({
  id: item.id,
  fullName: item.full_name,
  email: item.email,
  role: item.role,
  departmentId: item.department_id,
  mustChangePassword: Boolean(item.must_change_password),
  isActive: Boolean(item.is_active),
  deactivatedAt: item.deactivated_at || null,
})

const mapUserToApi = (userData) => {
  const payload = {}
  if (userData.fullName !== undefined) {
    payload.full_name = userData.fullName.trim()
  }
  if (userData.email !== undefined) {
    payload.email = userData.email.trim().toLowerCase()
  }
  if (userData.departmentId !== undefined) {
    payload.department_id = userData.departmentId
  }
  if (userData.role !== undefined) {
    payload.role = userData.role
  }
  return payload
}

export const getUsers = async () => {
  const data = await request('/users')
  return Array.isArray(data) ? data.map(mapUserFromApi) : []
}

export const getUserById = async (userId) => {
  return mapUserFromApi(await request(`/users/${userId}`))
}

export const updateUser = async (userId, userData) => {
  const payload = mapUserToApi(userData)
  const data = await patchJson(`/users/${userId}`, payload)
  return mapUserFromApi(data)
}

export const deactivateUser = async (userId) => {
  const data = await patchJson(`/users/${userId}/deactivate`, {})
  return mapUserFromApi(data)
}
