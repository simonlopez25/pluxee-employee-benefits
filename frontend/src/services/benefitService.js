import { getJson, patchJson, postJson, putJson } from './http'

const mapBenefitFromApi = (item) => ({
  id: item.id,
  name: item.name,
  description: item.description || '',
  isBasic: Boolean(item.is_basic),
  isActive: Boolean(item.is_active),
})

const mapBenefitToApi = (benefitData) => {
  const payload = {}
  if (benefitData.name !== undefined) payload.name = benefitData.name.trim()
  if (benefitData.description !== undefined) payload.description = benefitData.description.trim()
  if (benefitData.isBasic !== undefined) payload.is_basic = Boolean(benefitData.isBasic)
  else if (benefitData.is_basic !== undefined) payload.is_basic = Boolean(benefitData.is_basic)
  if (benefitData.isActive !== undefined) payload.is_active = Boolean(benefitData.isActive)
  else if (benefitData.is_active !== undefined) payload.is_active = Boolean(benefitData.is_active)
  return payload
}

export const getBenefits = async (filters = {}) => {
  const params = new URLSearchParams()
  const isActive = filters.isActive ?? filters.is_active
  const isBasic = filters.isBasic ?? filters.is_basic
  if (isActive !== undefined && isActive !== null) params.set('is_active', isActive)
  if (isBasic !== undefined && isBasic !== null) params.set('is_basic', isBasic)
  if (filters.orderBy) params.set('order_by', filters.orderBy)
  const query = params.toString()
  const data = await getJson(`/benefits${query ? `?${query}` : ''}`)
  return data.map(mapBenefitFromApi)
}

export const getBenefitById = async (benefitId) => {
  const data = await getJson(`/benefits/${benefitId}`)
  return mapBenefitFromApi(data)
}

export const createBenefit = async (benefitData) => {
  const data = await postJson('/benefits', mapBenefitToApi(benefitData))
  return mapBenefitFromApi(data)
}

export const updateBenefit = async (benefitId, benefitData) => {
  const data = await putJson(`/benefits/${benefitId}`, mapBenefitToApi(benefitData))
  return mapBenefitFromApi(data)
}

export const toggleBenefitStatus = async (benefitId, statusData) => {
  const payload = {}
  if (statusData.isActive !== undefined) payload.is_active = Boolean(statusData.isActive)
  else if (statusData.is_active !== undefined) payload.is_active = Boolean(statusData.is_active)
  if (statusData.isBasic !== undefined) payload.is_basic = Boolean(statusData.isBasic)
  else if (statusData.is_basic !== undefined) payload.is_basic = Boolean(statusData.is_basic)
  const data = await patchJson(`/benefits/${benefitId}`, payload)
  return mapBenefitFromApi(data)
}