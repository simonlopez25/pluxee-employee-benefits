const TOKEN_KEY = 'pluxee_token'
const USER_KEY = 'pluxee_user'

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY)
}

export function clearUser() {
  sessionStorage.removeItem(USER_KEY)
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

  const body = await response.json().catch(() => null)

  if (response.status === 401 && path !== '/login') {
    clearToken()
    clearUser()
    window.location.assign('/login')
    throw new ApiError('session_expired', 'La sesión ha caducado. Vuelve a iniciar sesión', 401)
  }

  if (
    response.status === 403 &&
    body?.error?.code === 'account_inactive' &&
    path !== '/login'
  ) {
    clearToken()
    clearUser()
    window.location.assign('/login')
    throw new ApiError(
      'account_inactive',
      'Tu cuenta está desactivada. Contacta con administración',
      403,
    )
  }

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