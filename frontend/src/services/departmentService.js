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

const mapDepartmentFromApi = (item) => ({
  id: item.id,
  name: item.name,
  currency: item.currency,
  isActive: Boolean(item.is_active),
  createdAt: item.created_at,
  // Añadido para la lista de departamentos (con fallback si viene de GET /{id}, POST o PUT)
  employeeCount: Number(item.employee_count ?? item.employeeCount ?? 0) || 0,
  packages: Array.isArray(item.packages)
    ? item.packages.map((pkg) => ({
        id: pkg.id,
        name: pkg.name,
      }))
    : [],
})

const mapDepartmentToApi = (departmentData) => ({
  name: departmentData.name.trim(),
  currency: departmentData.currency.trim().toUpperCase(),
})

export const getDepartments = async (filters = {}) => {
  const queryParams = {}
  if (filters.isActive !== undefined && filters.isActive !== null) {
    queryParams.is_active = filters.isActive
  }

  const url = getEndpointUrl('departments', queryParams)
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return Array.isArray(data) ? data.map(mapDepartmentFromApi) : []
}

export const getDepartmentById = async (departmentId) => {
  const url = getEndpointUrl(`departments/${departmentId}`)
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return mapDepartmentFromApi(data)
}

export const createDepartment = async (departmentData) => {
  const url = getEndpointUrl('departments')
  const payload = mapDepartmentToApi(departmentData)

  const response = await fetch(url, {
    method: 'POST',
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
  return mapDepartmentFromApi(data)
}

export const updateDepartment = async (departmentId, departmentData) => {
  const url = getEndpointUrl(`departments/${departmentId}`)
  const payload = mapDepartmentToApi(departmentData)

  const response = await fetch(url, {
    method: 'PUT',
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
  return mapDepartmentFromApi(data)
}