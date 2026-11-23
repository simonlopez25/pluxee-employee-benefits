import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { PackagesSection } from './PackagesSection'
import { getBenefits } from '../../../services/benefitService'
import {
  createPackage,
  getActiveDepartments,
  getPackages,
} from '../../../services/packageService'
import { ApiError } from '../../../services/http'

// Sustituimos los services por funciones falsas: el test no llama al backend
vi.mock('../../../services/packageService', () => ({
  getPackages: vi.fn(),
  getActiveDepartments: vi.fn(),
  createPackage: vi.fn(),
}))
vi.mock('../../../services/benefitService', () => ({ getBenefits: vi.fn() }))

const DEPARTMENTS = [{ id: 1, name: 'Ventas', is_active: true }]
const BENEFITS = [
  { id: 10, name: 'Comida' },
  { id: 20, name: 'Transporte' },
]
const MULTI_PACKAGE = {
  id: 5,
  name: 'Comida y transporte',
  description: null,
  default_amount: '100.00',
  department_id: 1,
  is_active: true,
  benefits: [
    { id: 10, name: 'Comida' },
    { id: 20, name: 'Transporte' },
  ],
  package_type: 'MULTI',
}

beforeEach(() => {
  vi.resetAllMocks()
  getActiveDepartments.mockResolvedValue(DEPARTMENTS)
  getBenefits.mockResolvedValue(BENEFITS)
})

afterEach(() => {
  cleanup()
})

// Rellena el formulario del modal con un paquete monobeneficio de Comida
async function fillMonoPackageForm(user) {
  await user.type(screen.getByLabelText(/Nombre del paquete/), 'Solo comida')
  await user.type(screen.getByLabelText(/Importe por empleado/), '50')
  await user.selectOptions(screen.getByLabelText(/Departamento/), '1')
  await user.click(screen.getByRole('checkbox', { name: 'Comida' }))
}

describe('PackagesSection', () => {
  it('muestra los paquetes con departamento, tipo, importe y beneficios', async () => {
    getPackages.mockResolvedValue([MULTI_PACKAGE])
    render(<PackagesSection />)

    expect(await screen.findByText('Comida y transporte')).toBeInTheDocument()
    expect(screen.getByText(/Ventas · Multibeneficio/)).toBeInTheDocument()
    expect(screen.getByText(/100,00\s€ por empleado/)).toBeInTheDocument()
    expect(screen.getByText('Comida · Transporte')).toBeInTheDocument()
  })

  it('muestra un aviso si no hay paquetes', async () => {
    getPackages.mockResolvedValue([])
    render(<PackagesSection />)

    expect(await screen.findByText('Todavía no hay paquetes creados.')).toBeInTheDocument()
  })

  it('muestra el error si falla la carga', async () => {
    getPackages.mockRejectedValue(new ApiError('unknown_error', 'Error inesperado', 500))
    render(<PackagesSection />)

    expect(await screen.findByRole('alert')).toHaveTextContent('Error inesperado')
  })

  it('crea un paquete y lo añade a la lista', async () => {
    const user = userEvent.setup()
    getPackages.mockResolvedValue([])
    createPackage.mockResolvedValue({
      ...MULTI_PACKAGE,
      id: 6,
      name: 'Solo comida',
      default_amount: '50.00',
      benefits: [{ id: 10, name: 'Comida' }],
      package_type: 'MONO',
    })
    render(<PackagesSection />)

    await user.click(await screen.findByRole('button', { name: /Nuevo paquete/ }))
    await fillMonoPackageForm(user)
    await user.click(screen.getByRole('button', { name: 'Crear paquete' }))

    expect(createPackage).toHaveBeenCalledWith({
      name: 'Solo comida',
      description: null,
      default_amount: '50',
      department_id: 1,
      benefit_ids: [10],
    })
    expect(await screen.findByText('Paquete "Solo comida" creado')).toBeInTheDocument()
    expect(screen.getByText(/Ventas · Monobeneficio/)).toBeInTheDocument()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('no llama al backend si falta un beneficio', async () => {
    const user = userEvent.setup()
    getPackages.mockResolvedValue([])
    render(<PackagesSection />)

    await user.click(await screen.findByRole('button', { name: /Nuevo paquete/ }))
    await user.type(screen.getByLabelText(/Nombre del paquete/), 'Sin beneficios')
    await user.type(screen.getByLabelText(/Importe por empleado/), '50')
    await user.selectOptions(screen.getByLabelText(/Departamento/), '1')
    await user.click(screen.getByRole('button', { name: 'Crear paquete' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Elige al menos un beneficio')
    expect(createPackage).not.toHaveBeenCalled()
  })

  it('muestra el 409 del backend dentro del modal', async () => {
    const user = userEvent.setup()
    getPackages.mockResolvedValue([])
    createPackage.mockRejectedValue(
      new ApiError(
        'conflict',
        'Ya existe un paquete con ese nombre en este departamento',
        409,
      ),
    )
    render(<PackagesSection />)

    await user.click(await screen.findByRole('button', { name: /Nuevo paquete/ }))
    await fillMonoPackageForm(user)
    await user.click(screen.getByRole('button', { name: 'Crear paquete' }))

    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent(
        'Ya existe un paquete con ese nombre en este departamento',
      ),
    )
    expect(screen.getByRole('dialog')).toBeInTheDocument()
  })
})