import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import Login from './Login'
import { useAuth } from '../../context/AuthContext'
import { ApiError } from '../../services/http'

const navigateMock = vi.fn()

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, useNavigate: () => navigateMock }
})

vi.mock('../../context/AuthContext', () => ({ useAuth: vi.fn() }))

function setupAuth(overrides = {}) {
  const loginMock = vi.fn()
  useAuth.mockReturnValue({
    user: null,
    login: loginMock,
    logout: vi.fn(),
    isAuthenticated: false,
    ...overrides,
  })
  return { loginMock }
}

beforeEach(() => {
  useAuth.mockReset()
  navigateMock.mockReset()
})

afterEach(() => {
  cleanup()
})

describe('Login', () => {
  it('renderiza el formulario de acceso', () => {
    setupAuth()
    render(<Login />)

    expect(screen.getByLabelText('Correo electrónico')).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('si ya hay sesión de admin redirige a /dashboard', () => {
    setupAuth({ user: { role: 'ADMIN' }, isAuthenticated: true })
    render(<Login />)

    expect(navigateMock).toHaveBeenCalledWith('/dashboard', { replace: true })
  })
  
  it('si ya hay sesión de empleado redirige a /empleado', () => {
    setupAuth({ user: { role: 'EMPLOYEE' }, isAuthenticated: true })
    render(<Login />)

    expect(navigateMock).toHaveBeenCalledWith('/empleado', { replace: true })
  })

  it('envía credenciales al hacer submit', async () => {
    const user = userEvent.setup()
    const { loginMock } = setupAuth()
    loginMock.mockResolvedValue({ role: 'EMPLOYEE' })
    render(<Login />)

    await user.type(screen.getByLabelText('Correo electrónico'), 'lucia.garcia@pluxee.test')
    await user.type(screen.getByLabelText('Contraseña'), 'Prueba123!')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(loginMock).toHaveBeenCalledWith('lucia.garcia@pluxee.test', 'Prueba123!')
  })

  it('muestra el mensaje de error devuelto por la API', async () => {
    const user = userEvent.setup()
    const { loginMock } = setupAuth()
    loginMock.mockRejectedValue(
      new ApiError('invalid_credentials', 'Correo o contraseña incorrectos', 401),
    )
    render(<Login />)

    await user.type(screen.getByLabelText('Correo electrónico'), 'a@b.c')
    await user.type(screen.getByLabelText('Contraseña'), 'mala')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Correo o contraseña incorrectos')).toBeInTheDocument()
  })

  it('muestra mensaje genérico si no hay conexión', async () => {
    const user = userEvent.setup()
    const { loginMock } = setupAuth()
    loginMock.mockRejectedValue(new TypeError('Failed to fetch'))
    render(<Login />)

    await user.type(screen.getByLabelText('Correo electrónico'), 'a@b.c')
    await user.type(screen.getByLabelText('Contraseña'), 'x')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(
      await screen.findByText('No se ha podido conectar con el servidor'),
    ).toBeInTheDocument()
  })

  it('deshabilita el botón y muestra "Entrando…" mientras envía', async () => {
    const user = userEvent.setup()
    const { loginMock } = setupAuth()
    let resolveLogin
    loginMock.mockReturnValue(new Promise((resolve) => { resolveLogin = resolve }))
    render(<Login />)

    await user.type(screen.getByLabelText('Correo electrónico'), 'a@b.c')
    await user.type(screen.getByLabelText('Contraseña'), 'x')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(screen.getByRole('button', { name: 'Entrando…' })).toBeDisabled()

    resolveLogin({ role: 'EMPLOYEE' })
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Entrar' })).not.toBeDisabled(),
    )
  })
})