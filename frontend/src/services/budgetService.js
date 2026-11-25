import { getJson, putJson } from './http'

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
  const query = period ? `?period=${encodeURIComponent(period)}` : ''
  const data = await getJson(`/budgets${query}`)
  return mapMonthlyOverviewFromApi(data)
}

export const saveGlobalBudget = async (period, totalAmount) => {
  const data = await putJson('/budgets/global', {
    period,
    total_amount: Number(totalAmount).toFixed(2),
  })
  return {
    id: data.id,
    period: data.period,
    totalAmount: Number(data.total_amount || 0),
    allocatedToDepartments: Number(data.allocated_to_departments || 0),
    unallocatedAmount: Number(data.unallocated_amount || 0),
  }
}

export const saveDepartmentBudget = async (departmentId, period, allocatedAmount) => {
  const data = await putJson(`/budgets/departments/${departmentId}`, {
    period,
    allocated_amount: Number(allocatedAmount).toFixed(2),
  })
  return mapDepartmentBudgetFromApi(data)
}

export const saveBenefitReferences = async (departmentId, period, references) => {
  const data = await putJson(`/budgets/departments/${departmentId}/references`, {
    period,
    references: references.map((item) => ({
      benefit_id: item.benefitId,
      indicative_amount: Number(item.indicativeAmount || 0).toFixed(2),
    })),
  })
  return mapDepartmentBudgetFromApi(data)
}

export const getActiveDepartments = async () => {
  const data = await getJson('/departments?is_active=true')
  return data.map((dept) => ({
    id: dept.id,
    name: dept.name,
    isActive: Boolean(dept.is_active),
  }))
}

export const getActiveBenefits = async () => {
  const data = await getJson('/benefits?is_active=true')
  return data.map((item) => ({
    id: item.id,
    name: item.name,
    description: item.description || '',
    isBasic: Boolean(item.is_basic),
    isActive: Boolean(item.is_active),
  }))
}