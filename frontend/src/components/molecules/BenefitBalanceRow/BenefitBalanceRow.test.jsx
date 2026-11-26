import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { BenefitBalanceRow } from './BenefitBalanceRow'

const BENEFIT = {
  benefit_id: 10,
  benefit_name: 'Comida',
  is_basic: true,
  consumed: '30.00',
  available: '120.50',
}

afterEach(() => {
  cleanup()
})

describe('BenefitBalanceRow', () => {
  it('muestra el disponible con formato español y dos decimales', () => {
    render(<BenefitBalanceRow benefit={BENEFIT} packageAssigned={150} />)

    expect(screen.getByText('Comida')).toBeInTheDocument()
    expect(screen.getByText('120,50 € disponibles')).toBeInTheDocument()
  })

  it('distingue un beneficio básico de uno flexible', () => {
    const { rerender } = render(
      <BenefitBalanceRow benefit={BENEFIT} packageAssigned={150} />,
    )
    expect(screen.getByText('Beneficio básico')).toBeInTheDocument()

    rerender(
      <BenefitBalanceRow benefit={{ ...BENEFIT, is_basic: false }} packageAssigned={150} />,
    )
    expect(screen.getByText('Beneficio flexible')).toBeInTheDocument()
  })

  it('rellena la barra según lo consumido sobre el total del paquete', () => {
    const { container } = render(
      <BenefitBalanceRow benefit={{ ...BENEFIT, consumed: '50.00' }} packageAssigned={100} />,
    )

    expect(container.querySelector('.progressSvgFill')).toHaveAttribute('width', '50')
  })

  it('con el paquete asignado a cero deja la barra vacía sin romperse', () => {
    const { container } = render(
      <BenefitBalanceRow benefit={BENEFIT} packageAssigned={0} />,
    )

    expect(container.querySelector('.progressSvgFill')).toHaveAttribute('width', '0')
  })
})