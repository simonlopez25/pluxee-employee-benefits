import { describe, expect, it } from 'vitest'

const getCurrentMonthFirstDay = (date = new Date()) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}-01`
}

const mergeDepartmentsWithBudgets = (departmentsList, monthlyBudgetsData) => {
  const budgetItems = Array.isArray(monthlyBudgetsData?.departments)
    ? monthlyBudgetsData.departments
    : []

  const budgetByDepartmentId = new Map()
  for (const item of budgetItems) {
    const deptId = item.department_id ?? item.departmentId
    if (deptId !== undefined && deptId !== null) {
      budgetByDepartmentId.set(Number(deptId), item)
    }
  }

  return (departmentsList || []).map((dept) => ({
    ...dept,
    monthlyBudget: budgetByDepartmentId.get(Number(dept.id)) ?? null,
  }))
}

const formatEmployeeLabel = (count = 0) => {
  const safeCount = Number(count) || 0
  return `${safeCount} ${safeCount === 1 ? 'empleado' : 'empleados'}`
}

const formatPackagesSummary = (packages = []) => {
  if (!Array.isArray(packages) || packages.length === 0) {
    return 'Sin paquetes'
  }
  const visibleNames = packages.slice(0, 2).map((pkg) => pkg.name)
  const extraCount = Math.max(0, packages.length - 2)
  return `${visibleNames.join(', ')}${extraCount > 0 ? ` +${extraCount}` : ''}`
}

describe('GroupsPage data & summary helpers', () => {
  const sampleDepartments = [
    {
      id: 1,
      name: 'Ingeniería',
      currency: 'EUR',
      isActive: true,
      employeeCount: 2,
      packages: [
        { id: 10, name: 'Transporte' },
        { id: 11, name: 'Formación' },
        { id: 12, name: 'Comida' },
      ],
    },
    {
      id: 2,
      name: 'Marketing',
      currency: 'EUR',
      isActive: true,
      employeeCount: 1,
      packages: [{ id: 13, name: 'Guardería' }],
    },
  ]

  it('formats current month first day as YYYY-MM-01', () => {
    expect(getCurrentMonthFirstDay(new Date('2026-11-23'))).toBe('2026-11-01')
  })

  it('merges monthly budgets by department_id and falls back to null when missing', () => {
    const monthlyOverview = {
      departments: [{ department_id: 1, amount: 4500 }],
    }

    const merged = mergeDepartmentsWithBudgets(sampleDepartments, monthlyOverview)
    expect(merged[0].monthlyBudget).toEqual({ department_id: 1, amount: 4500 })
    expect(merged[1].monthlyBudget).toBeNull()
  })

  it('handles null or empty monthly budgets response gracefully', () => {
    const merged = mergeDepartmentsWithBudgets(sampleDepartments, null)
    expect(merged.every((dept) => dept.monthlyBudget === null)).toBe(true)
  })

  it('formats employee counts with singular and plural', () => {
    expect(formatEmployeeLabel(0)).toBe('0 empleados')
    expect(formatEmployeeLabel(1)).toBe('1 empleado')
    expect(formatEmployeeLabel(2)).toBe('2 empleados')
  })

  it('formats up to 2 active packages and appends +N for extra packages', () => {
    expect(formatPackagesSummary([])).toBe('Sin paquetes')
    expect(formatPackagesSummary([{ id: 1, name: 'Guardería' }])).toBe('Guardería')
    expect(formatPackagesSummary(sampleDepartments[0].packages)).toBe(
      'Transporte, Formación +1',
    )
  })
})