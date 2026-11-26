import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { BenefitTotalsSummary } from './BenefitTotalsSummary'

const BENEFITS = [
  {
    benefit_id: 10,
    benefit_name: 'Comida',
    is_basic: true,
    consumed: '30.00',
    available: '120.00',
  },
  {
    benefit_id: 20,
    benefit_name: 'Transporte',
    is_basic: true,
    consumed: '30.00',
    available: '70.00',
  },
]

afterEach(() => {
  cleanup()
})

describe('BenefitTotalsSummary', () => {
  it('muestra el disponible de cada beneficio', () => {
    render(<BenefitTotalsSummary benefits={BENEFITS} />)

    const section = screen.getByRole('region', { name: 'Disponible por beneficio' })
    const items = within(section).getAllByRole('listitem')

    expect(items).toHaveLength(2)
    expect(items[0]).toHaveTextContent('Comida')
    expect(items[0]).toHaveTextContent('120,00 €')
    expect(items[1]).toHaveTextContent('Transporte')
    expect(items[1]).toHaveTextContent('70,00 €')
  })

  it('avisa de que los paquetes multibeneficio comparten saldo', () => {
    render(<BenefitTotalsSummary benefits={BENEFITS} />)

    expect(screen.getByText(/comparten saldo/)).toBeInTheDocument()
  })

  it('no renderiza nada si no hay beneficios', () => {
    const { container } = render(<BenefitTotalsSummary benefits={[]} />)

    expect(container).toBeEmptyDOMElement()
  })
})
