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

const mapDepartmentBudgetFromApi = (item) => ({
  id: item.id,
  departmentId: item.department_id,
  departmentName: item.department_name,
  period: item.period,
  allocatedAmount: Number(item.allocated_amount || 0),
  consumedAmount: Number(item.consumed_amount || 0),
  availableAmount: Number(item.available_amount || 0),
  usagePercentage: Number(item.usage_percentage || 0),
  benefitReferences: Array.isArray(item.benefit_references)
    ? item.benefit_references.map((ref) => ({
        benefitId: ref.benefit_id,
        benefitName: ref.benefit_name,
        indicativeAmount: Number(ref.indicative_amount || 0),
      }))
    : [],
})

const mapMonthlyOverviewFromApi = (data) => ({
  period: data.period,
  totalAmount: Number(data.total_amount || 0),
  allocatedToDepartments: Number(data.allocated_to_departments || 0),
  unallocatedAmount: Number(data.unallocated_amount || 0),
  departments: Array.isArray(data.departments)
    ? data.departments.map(mapDepartmentBudgetFromApi)
    : [],
})

export const getMonthlyBudgets = async (period) => {
  const queryParams = {}
  if (period) {
    queryParams.period = period
  }

  const url = getEndpointUrl('budgets', queryParams)
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return mapMonthlyOverviewFromApi(data)
}

export const saveGlobalBudget = async (period, totalAmount) => {
  const url = getEndpointUrl('budgets/global')
  const payload = {
    period,
    total_amount: Number(totalAmount).toFixed(2),
  }

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
  return {
    id: data.id,
    period: data.period,
    totalAmount: Number(data.total_amount || 0),
    allocatedToDepartments: Number(data.allocated_to_departments || 0),
    unallocatedAmount: Number(data.unallocated_amount || 0),
  }
}

export const saveDepartmentBudget = async (departmentId, period, allocatedAmount) => {
  const url = getEndpointUrl(`budgets/departments/${departmentId}`)
  const payload = {
    period,
    allocated_amount: Number(allocatedAmount).toFixed(2),
  }

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
  return mapDepartmentBudgetFromApi(data)
}

export const saveBenefitReferences = async (departmentId, period, references) => {
  const url = getEndpointUrl(`budgets/departments/${departmentId}/references`)
  const payload = {
    period,
    references: references.map((item) => ({
      benefit_id: item.benefitId,
      indicative_amount: Number(item.indicativeAmount || 0).toFixed(2),
    })),
  }

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
  return mapDepartmentBudgetFromApi(data)
}

export const getActiveDepartments = async () => {
  const url = getEndpointUrl('departments', { is_active: true })
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return data.map((dept) => ({
    id: dept.id,
    name: dept.name,
    isActive: Boolean(dept.is_active),
  }))
}

export const getActiveBenefits = async () => {
  const url = getEndpointUrl('benefits', { is_active: true })
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw await parseErrorResponse(response)
  }

  const data = await response.json()
  return data.map((item) => ({
    id: item.id,
    name: item.name,
    description: item.description || '',
    isBasic: Boolean(item.is_basic),
    isActive: Boolean(item.is_active),
  }))
}
