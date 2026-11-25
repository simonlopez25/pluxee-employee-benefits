import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ProtectedRoute from './ProtectedRoute'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

function renderWithRouter(initialPath, role) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route path="/login" element={<p>pantalla-login</p>} />
        <Route path="/dashboard" element={<p>panel-admin</p>} />
        <Route path="/empleado" element={<p>panel-empleado</p>} />
        <Route element={<ProtectedRoute role={role} />}>
          <Route path="/protegida" element={<p>contenido-protegido</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  useAuth.mockReset()
})

afterEach(() => {
  cleanup()
})

describe('ProtectedRoute', () => {
  it('sin sesión redirige a /login', () => {
    useAuth.mockReturnValue({ user: null, isAuthenticated: false })

    renderWithRouter('/protegida', undefined)

    expect(screen.getByText('pantalla-login')).toBeInTheDocument()
  })

  it('con rol correcto renderiza el contenido protegido', () => {
    useAuth.mockReturnValue({
      user: { role: 'EMPLOYEE' },
      isAuthenticated: true,
    })

    renderWithRouter('/protegida', 'EMPLOYEE')

    expect(screen.getByText('contenido-protegido')).toBeInTheDocument()
  })

  it('empleado en ruta de admin redirige a /empleado', () => {
    useAuth.mockReturnValue({
      user: { role: 'EMPLOYEE' },
      isAuthenticated: true,
    })

    renderWithRouter('/protegida', 'ADMIN')

    expect(screen.getByText('panel-empleado')).toBeInTheDocument()
  })

  it('admin en ruta de empleado redirige a /dashboard', () => {
    useAuth.mockReturnValue({
      user: { role: 'ADMIN' },
      isAuthenticated: true,
    })

    renderWithRouter('/protegida', 'EMPLOYEE')

    expect(screen.getByText('panel-admin')).toBeInTheDocument()
  })
})