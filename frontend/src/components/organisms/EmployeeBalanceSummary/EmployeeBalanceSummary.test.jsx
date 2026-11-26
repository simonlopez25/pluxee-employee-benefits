import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { EmployeeBalanceSummary } from './EmployeeBalanceSummary'

// Ejemplo del cliente: 100 € combo + 60 € mono comida, 90 € gastados
const BALANCE = {
  assigned_total: '160.00',
  approved_total: '60.00',
  pending_total: '30.00',
  consumed_total: '90.00',
  available_total: '70.00',
}

afterEach(() => {
  cleanup()
})

describe('EmployeeBalanceSummary', () => {
  it('muestra el saldo disponible, el asignado y el consumido', () => {
    render(<EmployeeBalanceSummary balance={BALANCE} />)

    expect(screen.getByText('Saldo disponible')).toBeInTheDocument()
    expect(screen.getByText('70,00 €')).toBeInTheDocument()

    expect(screen.getByText('Asignado').nextElementSibling).toHaveTextContent('160,00 €')
    expect(screen.getByText('Consumido').nextElementSibling).toHaveTextContent('90,00 €')
  })

  it('con saldo asignado a cero muestra todo a cero sin romperse', () => {
    render(
      <EmployeeBalanceSummary
        balance={{
          assigned_total: '0.00',
          approved_total: '0.00',
          pending_total: '0.00',
          consumed_total: '0.00',
          available_total: '0.00',
        }}
      />,
    )

    expect(screen.getByText('Saldo disponible').nextElementSibling).toHaveTextContent('0,00 €')
  })
})
