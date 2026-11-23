const getEndpointUrl = (path, params = {}) => {
  const rawBase = import.meta.env.VITE_API_URL || ''
  const apiBase = rawBase ? rawBase.replace(/\/+$/, '') : ''
  const cleanPath = path.replace(/^\/+/, '')
  const hasApiPrefix = apiBase.endsWith('/api')
  const baseUrlString = apiBase
    ? (hasApiPrefix ? `${apiBase}/${cleanPath}` : `${apiBase}/api/${cleanPath}`)
    : `/api/${cleanPath}`

  const url = new URL(baseUrlString, window.location.origin)
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.append(key, String(value))
    }
  })
  return url.toString()
}

const parseErrorResponse = async (response) => {
  try {
    const errorData = await response.json()
    if (errorData?.error?.message) {
      const error = new Error(errorData.error.message)
      error.status = response.status
      error.code = errorData.error.code
      return error
    }
    if (Array.isArray(errorData?.detail) && errorData.detail.length > 0) {
      const validationMessage = errorData.detail.map((item) => item.msg).join(', ')
      const error = new Error(validationMessage)
      error.status = response.status
      return error
    }
    if (typeof errorData?.detail === 'string') {
      const error = new Error(errorData.detail)
      error.status = response.status
      return error
    }
  } catch (parseError) {
    void parseError
  }
  const genericError = new Error(`Error ${response.status}: ${response.statusText}`)
  genericError.status = response.status
  return genericError
}

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
  const url = getEndpointUrl('users')
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return Array.isArray(data) ? data.map(mapUserFromApi) : []
}

export const getUserById = async (userId) => {
  const url = getEndpointUrl(`users/${userId}`)
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return mapUserFromApi(data)
}

export const updateUser = async (userId, userData) => {
  const url = getEndpointUrl(`users/${userId}`)
  const payload = mapUserToApi(userData)

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return mapUserFromApi(data)
}

export const deactivateUser = async (userId) => {
  const url = getEndpointUrl(`users/${userId}/deactivate`)

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({}),
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return mapUserFromApi(data)
}
