import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { EmployeeHomePage } from './EmployeeHomePage'
import { useAuth } from '../../context/AuthContext'
import { getMyBalance } from '../../services/balanceService'

vi.mock('../../context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../services/balanceService', () => ({ getMyBalance: vi.fn() }))

const BALANCE = {
  period: '2026-11-01',
  assigned_total: '160.00',
  approved_total: '60.00',
  pending_total: '30.00',
  consumed_total: '90.00',
  available_total: '70.00',
  by_benefit: [],
  packages: [],
}

function renderPage() {
  return render(
    <MemoryRouter>
      <EmployeeHomePage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.resetAllMocks()
  useAuth.mockReturnValue({ user: { full_name: 'Ana López' } })
})

afterEach(() => {
  cleanup()
})

describe('EmployeeHomePage', () => {
  it('muestra un aviso mientras carga el saldo', () => {
    getMyBalance.mockReturnValue(new Promise(() => {}))
    renderPage()

    expect(screen.getByText('Cargando tu saldo…')).toBeInTheDocument()
  })

  it('saluda por el nombre y muestra disponible, asignado y consumido', async () => {
    getMyBalance.mockResolvedValue(BALANCE)
    renderPage()

    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Hola, Ana')
    expect(screen.getByText('70,00 €')).toBeInTheDocument()
    expect(screen.getByText('Asignado').nextElementSibling).toHaveTextContent('160,00 €')
    expect(screen.getByText('Consumido').nextElementSibling).toHaveTextContent('90,00 €')
  })

  it('enlaza con la pantalla de beneficios y paquetes', async () => {
    getMyBalance.mockResolvedValue(BALANCE)
    renderPage()

    const link = await screen.findByRole('link', { name: /Mis beneficios/ })
    expect(link).toHaveAttribute('href', '/empleado/beneficios')
  })

  it('muestra el error si falla la carga del saldo', async () => {
    getMyBalance.mockRejectedValue(new Error('fallo'))
    renderPage()

    expect(
      await screen.findByText('No se pudo cargar tu saldo. Inténtalo de nuevo.'),
    ).toBeInTheDocument()
  })
})
