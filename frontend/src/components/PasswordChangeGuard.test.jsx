import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import PasswordChangeGuard from './PasswordChangeGuard'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

function setupAuth(overrides = {}) {
  useAuth.mockReturnValue({
    user: { role: 'EMPLOYEE' },
    mustChangePassword: false,
    ...overrides,
  })
}

beforeEach(() => {
  useAuth.mockReset()
})

afterEach(() => {
  cleanup()
})

describe('PasswordChangeGuard', () => {
  it('redirige a /change-password cuando must_change_password=true', () => {
    setupAuth({ mustChangePassword: true })
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route element={<PasswordChangeGuard />}>
            <Route path="/admin" element={<div>Admin</div>} />
          </Route>
          <Route path="/change-password" element={<div>Cambio</div>} />
        </Routes>
      </MemoryRouter>,
    )
    // La redirección replace() hace que el contenido de /admin no se muestre
    expect(screen.queryByText('Admin')).not.toBeInTheDocument()
    expect(screen.getByText('Cambio')).toBeInTheDocument()
  })

  it('permite el acceso cuando must_change_password=false', () => {
    setupAuth({ mustChangePassword: false })
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route element={<PasswordChangeGuard />}>
            <Route path="/admin" element={<div>Admin</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )
    expect(screen.getByText('Admin')).toBeInTheDocument()
  })
})