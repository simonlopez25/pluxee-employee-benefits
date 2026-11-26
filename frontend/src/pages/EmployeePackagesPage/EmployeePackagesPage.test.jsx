import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { EmployeePackagesPage } from './EmployeePackagesPage'
import { getMyBalance } from '../../services/balanceService'

// Sustituimos el service por una función falsa: el test no llama al backend
vi.mock('../../services/balanceService', () => ({ getMyBalance: vi.fn() }))

const COMIDA = {
  benefit_id: 10,
  benefit_name: 'Comida',
  is_basic: true,
  consumed: '30.00',
  available: '70.00',
}
const TRANSPORTE = {
  benefit_id: 20,
  benefit_name: 'Transporte',
  is_basic: true,
  consumed: '30.00',
  available: '70.00',
}

// 100 € combo comida+transporte, 50 € mono comida, 30 € gastados en transporte
const BALANCE = {
  period: '2026-11-01',
  assigned_total: '150.00',
  approved_total: '30.00',
  pending_total: '0.00',
  consumed_total: '30.00',
  available_total: '120.00',
  by_benefit: [
    { ...COMIDA, consumed: '30.00', available: '120.00' },
    { ...TRANSPORTE, available: '70.00' },
  ],
  packages: [
    {
      package_id: 2,
      package_name: 'Mono comida',
      assigned: '50.00',
      approved: '0.00',
      pending: '0.00',
      consumed: '0.00',
      available: '50.00',
      benefits: [{ ...COMIDA, consumed: '0.00', available: '50.00' }],
    },
    {
      package_id: 1,
      package_name: 'Combo comida y transporte',
      assigned: '100.00',
      approved: '30.00',
      pending: '0.00',
      consumed: '30.00',
      available: '70.00',
      benefits: [COMIDA, TRANSPORTE],
    },
  ],
}

const EMPTY_BALANCE = {
  period: '2026-11-01',
  assigned_total: '0.00',
  approved_total: '0.00',
  pending_total: '0.00',
  consumed_total: '0.00',
  available_total: '0.00',
  by_benefit: [],
  packages: [],
}

beforeEach(() => {
  vi.resetAllMocks()
})

afterEach(() => {
  cleanup()
})

describe('EmployeePackagesPage', () => {
  it('muestra un aviso mientras carga', () => {
    getMyBalance.mockReturnValue(new Promise(() => {}))
    render(<EmployeePackagesPage />)

    expect(screen.getByText('Cargando tus beneficios…')).toBeInTheDocument()
  })

  it('muestra el máximo disponible por beneficio', async () => {
    getMyBalance.mockResolvedValue(BALANCE)
    render(<EmployeePackagesPage />)

    const totals = await screen.findByRole('region', { name: 'Disponible por beneficio' })
    const items = within(totals).getAllByRole('listitem')

    expect(items[0]).toHaveTextContent('Comida')
    expect(items[0]).toHaveTextContent('120,00 €')
    expect(items[1]).toHaveTextContent('Transporte')
    expect(items[1]).toHaveTextContent('70,00 €')
  })

  it('lista los paquetes ordenados por importe asignado, de mayor a menor', async () => {
    getMyBalance.mockResolvedValue(BALANCE)
    render(<EmployeePackagesPage />)

    await screen.findByText('Combo comida y transporte')
    const titles = screen
      .getAllByRole('heading', { level: 2 })
      .map((heading) => heading.textContent)

    expect(titles).toEqual([
      'Disponible por beneficio',
      'Combo comida y transporte',
      'Mono comida',
    ])
  })

  it('indica que el saldo es mensual', async () => {
    getMyBalance.mockResolvedValue(BALANCE)
    render(<EmployeePackagesPage />)

    expect(await screen.findByText(/este mes/)).toBeInTheDocument()
  })

  it('muestra un aviso si no hay paquetes asignados', async () => {
    getMyBalance.mockResolvedValue(EMPTY_BALANCE)
    render(<EmployeePackagesPage />)

    expect(await screen.findByText('No tienes paquetes asignados.')).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Disponible por beneficio' })).not.toBeInTheDocument()
  })

  it('muestra el error si falla la carga', async () => {
    getMyBalance.mockRejectedValue(new Error('fallo'))
    render(<EmployeePackagesPage />)

    expect(await screen.findByText('No se pudieron cargar tus beneficios.')).toBeInTheDocument()
  })
})
