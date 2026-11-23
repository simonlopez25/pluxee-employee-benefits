import { cleanup, render, screen, within, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { EmployeesPage } from './EmployeesPage'
import { useAuth } from '../../context/AuthContext'

const mockGetUsers = vi.fn()
const mockGetDepartments = vi.fn()
const mockUpdateUser = vi.fn()
const mockDeactivateUser = vi.fn()

vi.mock('../../services/userService', () => ({
  getUsers: () => mockGetUsers(),
  updateUser: (id, data) => mockUpdateUser(id, data),
  deactivateUser: (id) => mockDeactivateUser(id),
}))

vi.mock('../../services/departmentService', () => ({
  getDepartments: () => mockGetDepartments(),
}))

vi.mock('../../context/AuthContext', () => ({ useAuth: vi.fn() }))

function setupAuth(overrides = {}) {
  useAuth.mockReturnValue({
    user: { id: 100, role: 'ADMIN', fullName: 'Admin User' },
    isAuthenticated: true,
    ...overrides,
  })
}

const sampleEmployees = [
  {
    id: 1,
    fullName: 'Lucía García',
    email: 'lucia.garcia@empresa.com',
    role: 'EMPLOYEE',
    departmentId: 1,
    isActive: true,
    deactivatedAt: null,
  },
  {
    id: 2,
    fullName: 'Carlos Ruiz',
    email: 'carlos.ruiz@empresa.com',
    role: 'EMPLOYEE',
    departmentId: null,
    isActive: false,
    deactivatedAt: '2026-11-20T10:30:00Z',
  },
  {
    id: 100,
    fullName: 'Admin User',
    email: 'admin@empresa.com',
    role: 'ADMIN',
    departmentId: null,
    isActive: true,
    deactivatedAt: null,
  },
]

const sampleDepartments = [{ id: 1, name: 'Ingeniería' }]

beforeEach(() => {
  vi.resetAllMocks()
  setupAuth()
  mockGetUsers.mockResolvedValue(sampleEmployees)
  mockGetDepartments.mockResolvedValue(sampleDepartments)
  mockUpdateUser.mockResolvedValue(undefined)
  mockDeactivateUser.mockResolvedValue(undefined)
})

afterEach(() => {
  cleanup()
})

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/admin/employees']}>
      <EmployeesPage />
    </MemoryRouter>,
  )
}

function getRowByName(name) {
  return screen.getByText(name).closest('tr')
}

describe('EmployeesPage', () => {
  it('muestra esqueletos mientras carga', async () => {
    mockGetUsers.mockResolvedValueOnce(new Promise(() => {}))
    const { container } = render(
      <MemoryRouter initialEntries={['/admin/employees']}>
        <EmployeesPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Empleados' })).toBeInTheDocument()
    expect(
      container.querySelectorAll('.employeesSkeletonRow').length > 0,
    ).toBe(true)
  })

  it('renderiza la tabla de empleados activos e inactivos', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Lucía García')).toBeInTheDocument(),
    )
    expect(screen.getByText('Carlos Ruiz')).toBeInTheDocument()
    expect(screen.getByText('Admin User')).toBeInTheDocument()

    const activeBadges = screen.getAllByText('Activo')
    expect(activeBadges).toHaveLength(2)
    const carlosRow = getRowByName('Carlos Ruiz')
    expect(carlosRow).toHaveTextContent('Inactivo')
  })

  it('muestra el conteo de empleados', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText(/3\s*empleados/)).toBeInTheDocument(),
    )
  })

  it('muestra el departamento asignado', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Ingeniería')).toBeInTheDocument(),
    )
  })

  it('muestra guión cuando no hay departamento', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Carlos Ruiz')).toBeInTheDocument(),
    )
    const row = getRowByName('Carlos Ruiz')
    expect(row).toHaveTextContent('—')
  })

  it('muestra fecha de baja para empleados inactivos', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Carlos Ruiz')).toBeInTheDocument(),
    )
    expect(screen.getByText(/20\/11\/2026/)).toBeInTheDocument()
  })

  it('el administrador actual no puede darse de baja a sí mismo', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Admin User')).toBeInTheDocument(),
    )
    const adminRow = getRowByName('Admin User')
    expect(adminRow).toHaveTextContent('Tú (administrador)')
    expect(adminRow.querySelector('button')).not.toBeNull()
    expect(within(adminRow).queryByText('Dar de baja')).not.toBeInTheDocument()
  })

  it('los empleados activos tienen botón Editar y Dar de baja', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Lucía García')).toBeInTheDocument(),
    )
    const luciaRow = getRowByName('Lucía García')
    expect(within(luciaRow).getByText('Editar')).toBeInTheDocument()
    expect(within(luciaRow).getByText('Dar de baja')).toBeInTheDocument()
  })

  it('abre el modal de edición al hacer clic en Editar', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Lucía García')).toBeInTheDocument(),
    )
    const luciaRow = getRowByName('Lucía García')
    await userEvent.click(within(luciaRow).getByText('Editar'))

    expect(
      screen.getByRole('heading', { name: /editar empleado/i }),
    ).toBeInTheDocument()
  })

  it('abre el modal de baja al hacer clic en Dar de baja', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Lucía García')).toBeInTheDocument(),
    )
    const luciaRow = getRowByName('Lucía García')
    await userEvent.click(within(luciaRow).getByText('Dar de baja'))

    expect(
      screen.getByText(/dar de baja a lucía garcía/i),
    ).toBeInTheDocument()
  })

  it('muestra estado vacío cuando no hay empleados', async () => {
    mockGetUsers.mockResolvedValueOnce([])
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('No hay empleados registrados')).toBeInTheDocument(),
    )
  })

  it('muestra mensaje de error y botón reintentar al fallar la carga', async () => {
    mockGetUsers.mockRejectedValueOnce(
      new Error('Error al cargar la plantilla de empleados'),
    )
    renderPage()

    await waitFor(() =>
      expect(screen.getByText(/error al cargar/i)).toBeInTheDocument(),
    )
    expect(
      screen.getByRole('button', { name: 'Reintentar' }),
    ).toBeInTheDocument()
  })

  it('actualiza un empleado y recarga al guardar cambios', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Lucía García')).toBeInTheDocument(),
    )
    const luciaRow = getRowByName('Lucía García')
    await userEvent.click(within(luciaRow).getByText('Editar'))

    const nameInput = screen.getByLabelText(/nombre completo/i)
    await userEvent.clear(nameInput)
    await userEvent.type(nameInput, 'Lucía García Modificada')

    await userEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    await waitFor(() =>
      expect(mockUpdateUser).toHaveBeenCalledWith(1, expect.any(Object)),
    )
    expect(screen.getByText('Empleado actualizado correctamente')).toBeInTheDocument()
  })

  it('da de baja a un empleado al confirmar', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Lucía García')).toBeInTheDocument(),
    )
    const luciaRow = getRowByName('Lucía García')
    await userEvent.click(within(luciaRow).getByText('Dar de baja'))

    await userEvent.click(
      within(screen.getByRole('dialog')).getByRole('button', {
        name: /dar de baja/i,
      }),
    )

    await waitFor(() =>
      expect(mockDeactivateUser).toHaveBeenCalledWith(1),
    )
    expect(screen.getByText('Empleado dado de baja correctamente')).toBeInTheDocument()
  })

  it('no muestra botón de baja para el administrador actual en su fila', async () => {
    renderPage()

    await waitFor(() =>
      expect(screen.getByText('Admin User')).toBeInTheDocument(),
    )
    const adminRow = getRowByName('Admin User')
    expect(within(adminRow).queryByText('Dar de baja')).not.toBeInTheDocument()
  })
})
