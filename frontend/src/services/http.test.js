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

  it('un 403 de cuenta inactiva lanza account_inactive, borra la sesión y redirige a login', async () => {
    setToken('valido')
    sessionStorage.setItem('pluxee_user', JSON.stringify({ id: 2, role: 'EMPLOYEE' }))

    fetchMock.mockResolvedValue(
      jsonResponse(403, {
        error: { code: 'account_inactive', message: 'Tu cuenta está desactivada. Contacta con administración' },
      }),
    )

    const err = await getJson('/me').catch((e) => e)

    expect(err).toBeInstanceOf(ApiError)
    expect(err.code).toBe('account_inactive')
    expect(err.status).toBe(403)
    expect(getToken()).toBeNull()
    expect(sessionStorage.getItem('pluxee_user')).toBeNull()
  })

  it('ante 422 del backend informa el campo y el mensaje', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(422, {
        detail: [
          { type: 'string_type', loc: ['body', 'name'], msg: 'Input should be a valid string' },
        ],
      }),
    )

    const err = await postJson('/benefits', { name: 1 }).catch((e) => e)

    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(422)
    expect(err.code).toBe('unknown_error')
    expect(err.message).toBe('name: Input should be a valid string')
  })

  it('ante varios errores de validación los une en un solo mensaje', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(422, {
        detail: [
          { type: 'missing', loc: ['body', 'name'], msg: 'Field required' },
          { type: 'missing', loc: ['body', 'currency'], msg: 'Field required' },
        ],
      }),
    )

    const err = await postJson('/departments', {}).catch((e) => e)

    expect(err.message).toBe('name: Field required, currency: Field required')
  })

  it('ante un 404 con detail de texto devuelve ese texto', async () => {
    fetchMock.mockResolvedValue(jsonResponse(404, { detail: 'Package not found' }))

    const err = await getJson('/packages/999').catch((e) => e)

    expect(err.status).toBe(404)
    expect(err.message).toBe('Package not found')
  })

  it('un error sin formato de error lanza unknown_error', async () => {
    fetchMock.mockResolvedValue(jsonResponse(500, null))

    const err = await getJson('/benefits').catch((e) => e)

    expect(err.code).toBe('unknown_error')
    expect(err.message).toBe('Error inesperado')
    expect(err.status).toBe(500)
  })
})