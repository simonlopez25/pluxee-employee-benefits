import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { PackageBalanceCard } from './PackageBalanceCard'

// Paquete multibeneficio de 100 € con 30 € gastados (20 aprobados y 10 pendientes)
const COMBO_PACKAGE = {
  package_id: 1,
  package_name: 'Comida y transporte',
  assigned: '100.00',
  approved: '20.00',
  pending: '10.00',
  consumed: '30.00',
  available: '70.00',
  benefits: [
    {
      benefit_id: 10,
      benefit_name: 'Comida',
      is_basic: true,
      consumed: '30.00',
      available: '70.00',
    },
    {
      benefit_id: 20,
      benefit_name: 'Transporte',
      is_basic: true,
      consumed: '30.00',
      available: '70.00',
    },
  ],
}

afterEach(() => {
  cleanup()
})

describe('PackageBalanceCard', () => {
  it('muestra el nombre del paquete y el total asignado', () => {
    render(<PackageBalanceCard packageBalance={COMBO_PACKAGE} />)

    expect(
      screen.getByRole('heading', { name: 'Comida y transporte' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Total asignado').nextElementSibling).toHaveTextContent(
      '100,00 €',
    )
  })

  it('en un paquete multibeneficio todos los beneficios comparten el mismo disponible', () => {
    render(<PackageBalanceCard packageBalance={COMBO_PACKAGE} />)

    expect(screen.getByText('Comida')).toBeInTheDocument()
    expect(screen.getByText('Transporte')).toBeInTheDocument()
    expect(screen.getAllByText('70,00 € disponibles')).toHaveLength(2)
  })

  it('no muestra ningún estado fijo del paquete', () => {
    render(<PackageBalanceCard packageBalance={COMBO_PACKAGE} />)

    expect(screen.queryByText('Activo')).not.toBeInTheDocument()
  })
})