import { cleanup, renderHook, act } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthProvider, useAuth } from './AuthContext'
import { postJson, setToken } from '../services/http'

vi.mock('../services/http', async (importOriginal) => {
  const actual = await importOriginal()
  return { ...actual, postJson: vi.fn() }
})

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>

const lucia = { id: 2, full_name: 'Lucía García', email: 'lucia.garcia@pluxee.test', role: 'EMPLOYEE' }

beforeEach(() => {
  sessionStorage.clear()
  postJson.mockReset()
})

afterEach(() => {
  cleanup()
})

describe('AuthContext', () => {
  it('arranca sin sesión cuando no hay nada en sessionStorage', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('rehidrata la sesión existente (token + usuario)', () => {
    setToken('token-vigente')
    sessionStorage.setItem('pluxee_user', JSON.stringify(lucia))

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user.email).toBe('lucia.garcia@pluxee.test')
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('ignora el usuario guardado si falta el token', () => {
    sessionStorage.setItem('pluxee_user', JSON.stringify(lucia))

    const { result } = renderHook(() => useAuth(), { wrapper })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('login guarda token y usuario, y devuelve el usuario', async () => {
    postJson.mockResolvedValue({ access_token: 'tok-nuevo', user: lucia })
    const { result } = renderHook(() => useAuth(), { wrapper })

    let returned
    await act(async () => {
      returned = await result.current.login('lucia.garcia@pluxee.test', 'Prueba123!')
    })

    expect(postJson).toHaveBeenCalledWith('/login', {
      email: 'lucia.garcia@pluxee.test',
      password: 'Prueba123!',
    })
    expect(returned).toEqual(lucia)
    expect(result.current.user).toEqual(lucia)
    expect(result.current.isAuthenticated).toBe(true)
    expect(sessionStorage.getItem('pluxee_token')).toBe('tok-nuevo')
    expect(JSON.parse(sessionStorage.getItem('pluxee_user'))).toEqual(lucia)
  })

  it('si el login falla no se guarda nada y el error se propaga', async () => {
    postJson.mockRejectedValue(new Error('invalid_credentials'))
    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await expect(result.current.login('a@b.c', 'mala')).rejects.toThrow('invalid_credentials')
    })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(sessionStorage.getItem('pluxee_token')).toBeNull()
    expect(sessionStorage.getItem('pluxee_user')).toBeNull()
  })

  it('logout limpia token, usuario y estado', async () => {
    setToken('token-vigente')
    sessionStorage.setItem('pluxee_user', JSON.stringify(lucia))
    const { result } = renderHook(() => useAuth(), { wrapper })

    act(() => {
      result.current.logout()
    })

    expect(result.current.user).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
    expect(sessionStorage.getItem('pluxee_token')).toBeNull()
    expect(sessionStorage.getItem('pluxee_user')).toBeNull()
  })

  it('useAuth fuera de AuthProvider lanza error claro', () => {
    expect(() => renderHook(() => useAuth())).toThrow(
      'useAuth debe usarse dentro de AuthProvider',
    )
  })
})