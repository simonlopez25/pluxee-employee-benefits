const TOKEN_KEY = 'pluxee_token'

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  constructor(code, message, status) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

export async function request(path, options = {}) {
  const token = getToken()
  const headers = new Headers(options.headers || {})
  headers.set('Content-Type', 'application/json')

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`/api${path}`, {
    ...options,
    headers,
  })

  if (response.status === 401 && path !== '/login') {
    clearToken()
    window.location.assign('/login')
    throw new ApiError('session_expired', 'La sesión ha caducado. Vuelve a iniciar sesión', 401)
  }

  const body = await response.json().catch(() => null)

  if (!response.ok) {
    const error = body?.error
    throw new ApiError(
      error?.code || 'unknown_error',
      error?.message || 'Error inesperado',
      response.status,
    )
  }

  return body
}

export function getJson(path) {
  return request(path)
}

export function postJson(path, data) {
  return request(path, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function patchJson(path, data) {
  return request(path, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export function putJson(path, data) {
  return request(path, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}