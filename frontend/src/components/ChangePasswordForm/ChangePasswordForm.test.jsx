import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ChangePasswordForm from './ChangePasswordForm'
import { useAuth } from '../../context/AuthContext'
import { patchJson } from '../../services/http'
import { ApiError } from '../../services/http'

vi.mock('../../context/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../services/http', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, patchJson: vi.fn() }
})

const employeeUser = { id: 2, full_name: 'Lucía', email: 'lucia@pluxee.test', role: 'EMPLOYEE', must_change_password: false }

function setupAuth(overrides = {}) {
  const updateMustChangePasswordMock = vi.fn()
  useAuth.mockReturnValue({
    user: employeeUser,
    updateMustChangePassword: updateMustChangePasswordMock,
    ...overrides,
  })
  return { updateMustChangePasswordMock }
}

beforeEach(() => {
  useAuth.mockReset()
  patchJson.mockReset()
})

afterEach(() => {
  cleanup()
})

describe('ChangePasswordForm', () => {
  it('renderiza los campos y el botón', () => {
    setupAuth()
    render(<ChangePasswordForm isForced={false} />)

    expect(screen.getByLabelText('Contraseña actual')).toBeInTheDocument()
    expect(screen.getByLabelText('Nueva contraseña')).toBeInTheDocument()
    expect(screen.getByLabelText('Confirmar nueva contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Cambiar contraseña' })).toBeInTheDocument()
  })

  it('muestra título de cambio obligatorio cuando isForced=true', () => {
    setupAuth()
    render(<ChangePasswordForm isForced={true} />)

    expect(screen.getByText('Cambio de contraseña obligatorio')).toBeInTheDocument()
  })

  it('muestra error cuando las contraseñas no coinciden', async () => {
    const user = userEvent.setup()
    setupAuth()
    render(<ChangePasswordForm isForced={false} />)

    await user.type(screen.getByLabelText('Contraseña actual'), 'Prueba123!')
    await user.type(screen.getByLabelText('Nueva contraseña'), 'NuevaContrasena123!')
    await user.type(screen.getByLabelText('Confirmar nueva contraseña'), 'Otra123!')
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }))

    expect(await screen.findByText('La nueva contraseña y su confirmación no coinciden')).toBeInTheDocument()
    expect(patchJson).not.toHaveBeenCalled()
  })

  it('muestra error cuando la nueva contraseña es demasiado corta', async () => {
    const user = userEvent.setup()
    setupAuth()
    render(<ChangePasswordForm isForced={false} />)

    await user.type(screen.getByLabelText('Contraseña actual'), 'Prueba123!')
    await user.type(screen.getByLabelText('Nueva contraseña'), 'corta')
    await user.type(screen.getByLabelText('Confirmar nueva contraseña'), 'corta')
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }))

    expect(await screen.findByText('La nueva contraseña debe tener al menos 10 caracteres')).toBeInTheDocument()
  })

  it('muestra error cuando la nueva iguala a la actual', async () => {
    const user = userEvent.setup()
    setupAuth()
    render(<ChangePasswordForm isForced={false} />)

    await user.type(screen.getByLabelText('Contraseña actual'), 'Prueba123!')
    await user.type(screen.getByLabelText('Nueva contraseña'), 'Prueba123!')
    await user.type(screen.getByLabelText('Confirmar nueva contraseña'), 'Prueba123!')
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }))

    expect(await screen.findByText('La nueva contraseña debe ser diferente a la actual')).toBeInTheDocument()
  })

  it('envía patchJson con los datos correctos y muestra éxito', async () => {
    const user = userEvent.setup()
    const { updateMustChangePasswordMock } = setupAuth()
    patchJson.mockResolvedValue({})
    const onSuccess = vi.fn()
    render(<ChangePasswordForm isForced={false} onSuccess={onSuccess} />)

    await user.type(screen.getByLabelText('Contraseña actual'), 'Prueba123!')
    await user.type(screen.getByLabelText('Nueva contraseña'), 'NuevaContrasena123!')
    await user.type(screen.getByLabelText('Confirmar nueva contraseña'), 'NuevaContrasena123!')
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }))

    expect(await screen.findByText('Contraseña actualizada correctamente')).toBeInTheDocument()
    expect(patchJson).toHaveBeenCalledWith('/users/me/password', {
      current_password: 'Prueba123!',
      new_password: 'NuevaContrasena123!',
      confirm_password: 'NuevaContrasena123!',
    })
    expect(updateMustChangePasswordMock).toHaveBeenCalledWith(false)
    expect(onSuccess).toHaveBeenCalled()
  })

  it('muestra error de la API cuando el cambio falla', async () => {
    const user = userEvent.setup()
    setupAuth()
    patchJson.mockRejectedValue(
      new ApiError('invalid_current_password', 'La contraseña actual no es correcta', 400),
    )
    render(<ChangePasswordForm isForced={false} />)

    await user.type(screen.getByLabelText('Contraseña actual'), 'mala')
    await user.type(screen.getByLabelText('Nueva contraseña'), 'NuevaContrasena123!')
    await user.type(screen.getByLabelText('Confirmar nueva contraseña'), 'NuevaContrasena123!')
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }))

    expect(await screen.findByText('La contraseña actual no es correcta')).toBeInTheDocument()
  })

  it('deshabilita el botón mientras envía', async () => {
    const user = userEvent.setup()
    setupAuth()
    let resolvePatch
    patchJson.mockReturnValue(new Promise((resolve) => { resolvePatch = resolve }))
    render(<ChangePasswordForm isForced={false} />)

    await user.type(screen.getByLabelText('Contraseña actual'), 'Prueba123!')
    await user.type(screen.getByLabelText('Nueva contraseña'), 'NuevaContrasena123!')
    await user.type(screen.getByLabelText('Confirmar nueva contraseña'), 'NuevaContrasena123!')
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }))

    expect(screen.getByRole('button', { name: 'Guardando...' })).toBeDisabled()

    resolvePatch({})
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Cambiar contraseña' })).not.toBeDisabled(),
    )
  })
})