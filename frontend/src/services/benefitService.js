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

const mapBenefitFromApi = (item) => ({
  id: item.id,
  name: item.name,
  description: item.description || '',
  isBasic: Boolean(item.is_basic),
  isActive: Boolean(item.is_active),
})

const mapBenefitToApi = (benefitData) => {
  const payload = {}
  if (benefitData.name !== undefined) {
    payload.name = benefitData.name.trim()
  }
  if (benefitData.description !== undefined) {
    payload.description = benefitData.description.trim()
  }
  if (benefitData.isBasic !== undefined) {
    payload.is_basic = Boolean(benefitData.isBasic)
  } else if (benefitData.is_basic !== undefined) {
    payload.is_basic = Boolean(benefitData.is_basic)
  }
  if (benefitData.isActive !== undefined) {
    payload.is_active = Boolean(benefitData.isActive)
  } else if (benefitData.is_active !== undefined) {
    payload.is_active = Boolean(benefitData.is_active)
  }
  return payload
}

export const getBenefits = async (filters = {}) => {
  const queryParams = {}
  if (filters.isActive !== undefined && filters.isActive !== null) {
    queryParams.is_active = filters.isActive
  } else if (filters.is_active !== undefined && filters.is_active !== null) {
    queryParams.is_active = filters.is_active
  }

  if (filters.isBasic !== undefined && filters.isBasic !== null) {
    queryParams.is_basic = filters.isBasic
  } else if (filters.is_basic !== undefined && filters.is_basic !== null) {
    queryParams.is_basic = filters.is_basic
  }

  if (filters.orderBy) {
    queryParams.order_by = filters.orderBy
  }

  const url = getEndpointUrl('benefits', queryParams)
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return data.map(mapBenefitFromApi)
}

export const getBenefitById = async (benefitId) => {
  const url = getEndpointUrl(`benefits/${benefitId}`)
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return mapBenefitFromApi(data)
}

export const createBenefit = async (benefitData) => {
  const url = getEndpointUrl('benefits')
  const payload = mapBenefitToApi(benefitData)

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
  return mapBenefitFromApi(data)
}

export const updateBenefit = async (benefitId, benefitData) => {
  const url = getEndpointUrl(`benefits/${benefitId}`)
  const payload = mapBenefitToApi(benefitData)

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
  return mapBenefitFromApi(data)
}

export const toggleBenefitStatus = async (benefitId, statusData) => {
  const url = getEndpointUrl(`benefits/${benefitId}`)
  const payload = {}

  if (statusData.isActive !== undefined) {
    payload.is_active = Boolean(statusData.isActive)
  } else if (statusData.is_active !== undefined) {
    payload.is_active = Boolean(statusData.is_active)
  }

  if (statusData.isBasic !== undefined) {
    payload.is_basic = Boolean(statusData.isBasic)
  } else if (statusData.is_basic !== undefined) {
    payload.is_basic = Boolean(statusData.is_basic)
  }

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
  return mapBenefitFromApi(data)
}
