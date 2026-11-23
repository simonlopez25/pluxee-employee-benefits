import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { firstDayOfMonth, MONTH_NAMES, MONTH_NAMES_CAPITALIZED } from '../../utils/dates'
import { formatCurrency } from '../../utils/format'

describe('BudgetsPage utilities', () => {
  describe('firstDayOfMonth', () => {
    it('returns YYYY-MM-01 for current date', () => {
      const result = firstDayOfMonth(new Date('2026-11-15'))
      expect(result).toBe('2026-11-01')
    })

    it('returns YYYY-MM-01 for any date in the month', () => {
      expect(firstDayOfMonth(new Date('2026-01-31'))).toBe('2026-01-01')
      expect(firstDayOfMonth(new Date('2026-12-25'))).toBe('2026-12-01')
    })

    it('uses current date when no argument provided', () => {
      const now = new Date()
      const expected = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
      expect(firstDayOfMonth()).toBe(expected)
    })
  })

  describe('MONTH_NAMES', () => {
    it('has 12 lowercase Spanish month names', () => {
      expect(MONTH_NAMES).toHaveLength(12)
      expect(MONTH_NAMES[0]).toBe('enero')
      expect(MONTH_NAMES[5]).toBe('junio')
      expect(MONTH_NAMES[11]).toBe('diciembre')
    })

    it('all entries are lowercase', () => {
      MONTH_NAMES.forEach((month) => {
        expect(month).toBe(month.toLowerCase())
      })
    })
  })

  describe('MONTH_NAMES_CAPITALIZED', () => {
    it('has 12 capitalized Spanish month names', () => {
      expect(MONTH_NAMES_CAPITALIZED).toHaveLength(12)
      expect(MONTH_NAMES_CAPITALIZED[0]).toBe('Enero')
      expect(MONTH_NAMES_CAPITALIZED[5]).toBe('Junio')
      expect(MONTH_NAMES_CAPITALIZED[11]).toBe('Diciembre')
    })

    it('all entries have first letter capitalized', () => {
      MONTH_NAMES_CAPITALIZED.forEach((month) => {
        expect(month[0]).toBe(month[0].toUpperCase())
        expect(month.slice(1)).toBe(month.slice(1).toLowerCase())
      })
    })
  })
})

describe('mergedDepartments logic (extracted from BudgetsPage)', () => {
  const activeDepartments = [
    { id: 1, name: 'Ventas', isActive: true },
    { id: 2, name: 'Marketing', isActive: true },
    { id: 3, name: 'IT', isActive: true },
  ]

  const overviewWithSomeBudgets = {
    period: '2026-11-01',
    departments: [
      {
        id: 10,
        departmentId: 1,
        departmentName: 'Ventas',
        period: '2026-11-01',
        allocatedAmount: 15000,
        consumedAmount: 5000,
        availableAmount: 10000,
        usagePercentage: 33.33,
        benefitReferences: [],
      },
    ],
  }

  function computeMergedDepartments(activeDepartments, overview, selectedPeriod) {
    if (!activeDepartments || activeDepartments.length === 0) {
      return overview?.departments || []
    }

    const budgetMap = new Map()
    if (overview?.departments) {
      overview.departments.forEach((dept) => {
        budgetMap.set(dept.departmentId, dept)
      })
    }

    return activeDepartments.map((dept) => {
      if (budgetMap.has(dept.id)) {
        return budgetMap.get(dept.id)
      }
      return {
        id: `unallocated-${dept.id}`,
        departmentId: dept.id,
        departmentName: dept.name,
        period: selectedPeriod,
        allocatedAmount: 0,
        consumedAmount: 0,
        availableAmount: 0,
        usagePercentage: 0,
        benefitReferences: [],
      }
    })
  }

  it('includes departments with budget from overview', () => {
    const result = computeMergedDepartments(activeDepartments, overviewWithSomeBudgets, '2026-11-01')

    const ventas = result.find((d) => d.departmentId === 1)
    expect(ventas).toBeDefined()
    expect(ventas.allocatedAmount).toBe(15000)
    expect(ventas.departmentName).toBe('Ventas')
  })

  it('includes departments WITHOUT budget with allocatedAmount = 0', () => {
    const result = computeMergedDepartments(activeDepartments, overviewWithSomeBudgets, '2026-11-01')

    const marketing = result.find((d) => d.departmentId === 2)
    expect(marketing).toBeDefined()
    expect(marketing.allocatedAmount).toBe(0)
    expect(marketing.departmentName).toBe('Marketing')
    expect(marketing.id).toBe('unallocated-2')
  })

  it('includes all active departments even if not in overview', () => {
    const result = computeMergedDepartments(activeDepartments, overviewWithSomeBudgets, '2026-11-01')

    expect(result).toHaveLength(3)
    expect(result.map((d) => d.departmentId).sort()).toEqual([1, 2, 3])
  })

  it('returns overview departments when no active departments', () => {
    const result = computeMergedDepartments([], overviewWithSomeBudgets, '2026-11-01')
    expect(result).toEqual(overviewWithSomeBudgets.departments)
  })
})

describe('formatCurrency utility', () => {
  it('formats numbers with 2 decimal places and EUR symbol', () => {
    // toLocaleString uses non-breaking space (U+00A0) before currency symbol
    expect(formatCurrency(15000)).toBe('15.000,00\u00A0\u20AC')
    expect(formatCurrency(15000.5)).toBe('15.000,50\u00A0\u20AC')
    expect(formatCurrency('15000')).toBe('15.000,00\u00A0\u20AC')
  })

  it('handles zero', () => {
    expect(formatCurrency(0)).toBe('0,00\u00A0\u20AC')
  })

  it('uses EUR currency by default', () => {
    expect(formatCurrency(1000)).toContain('\u20AC')
  })

  it('can format as decimal without currency symbol', () => {
    // decimal style doesn't include thousands separator by default
    expect(formatCurrency(1000, { style: 'decimal' })).toBe('1000,00')
  })
})