import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, clearToken, getJson, getToken, postJson, setToken } from './http'

function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  }
}

const fetchMock = vi.fn()

beforeEach(() => {
  sessionStorage.clear()
  fetchMock.mockReset()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('almacenamiento del token', () => {
  it('guarda, lee y borra el token en sessionStorage', () => {
    expect(getToken()).toBeNull()
    setToken('abc123')
    expect(getToken()).toBe('abc123')
    clearToken()
    expect(getToken()).toBeNull()
  })
})

describe('request', () => {
  it('hace GET a /api y devuelve el body', async () => {
    fetchMock.mockResolvedValue(jsonResponse(200, [{ id: 1 }]))

    const data = await getJson('/benefits')

    expect(data).toEqual([{ id: 1 }])
    const [url, opts] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/benefits')
    expect(opts.headers.get('Content-Type')).toBe('application/json')
    expect(opts.headers.get('Authorization')).toBeNull()
  })

  it('añade Authorization Bearer cuando hay token', async () => {
    setToken('token-de-prueba')
    fetchMock.mockResolvedValue(jsonResponse(200, { ok: true }))

    await getJson('/me')

    expect(fetchMock.mock.calls[0][1].headers.get('Authorization')).toBe(
      'Bearer token-de-prueba',
    )
  })

  it('envía POST con el body en JSON', async () => {
    fetchMock.mockResolvedValue(jsonResponse(200, { access_token: 't' }))

    await postJson('/login', { email: 'a@b.c', password: 'x' })

    const [url, opts] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/login')
    expect(opts.method).toBe('POST')
    expect(opts.body).toBe(JSON.stringify({ email: 'a@b.c', password: 'x' }))
  })

  it('ante 401 fuera de /login borra el token y lanza session_expired', async () => {
    setToken('caducado')
    fetchMock.mockResolvedValue(
      jsonResponse(401, { error: { code: 'invalid_token', message: 'Sesión no válida' } }),
    )

    const err = await getJson('/me').catch((e) => e)

    expect(err).toBeInstanceOf(ApiError)
    expect(err.code).toBe('session_expired')
    expect(err.status).toBe(401)
    expect(getToken()).toBeNull()
  })

  it('en /login un 401 conserva el código del backend (invalid_credentials)', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(401, {
        error: { code: 'invalid_credentials', message: 'Correo o contraseña incorrectos' },
      }),
    )

    const err = await postJson('/login', { email: 'a@b.c', password: 'mala' }).catch((e) => e)

    expect(err).toBeInstanceOf(ApiError)
    expect(err.code).toBe('invalid_credentials')
    expect(err.message).toBe('Correo o contraseña incorrectos')
  })

  it('un 403 de cuenta inactiva lanza account_inactive sin borrar el token', async () => {
    setToken('valido')
    fetchMock.mockResolvedValue(
      jsonResponse(403, {
        error: { code: 'account_inactive', message: 'Tu cuenta está desactivada. Contacta con administración' },
      }),
    )

    const err = await getJson('/me').catch((e) => e)

    expect(err.code).toBe('account_inactive')
    expect(err.status).toBe(403)
    expect(getToken()).toBe('valido')
  })

  it('un error sin formato de error lanza unknown_error', async () => {
    fetchMock.mockResolvedValue(jsonResponse(500, null))

    const err = await getJson('/benefits').catch((e) => e)

    expect(err.code).toBe('unknown_error')
    expect(err.message).toBe('Error inesperado')
    expect(err.status).toBe(500)
  })
})