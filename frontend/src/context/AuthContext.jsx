import { createContext, useContext, useState } from 'react'
import { clearToken, getToken, postJson, setToken } from '../services/http'

const USER_KEY = 'pluxee_user'

const AuthContext = createContext(null)

function readStoredUser() {
  try {
    const stored = sessionStorage.getItem(USER_KEY)
    if (getToken() && stored) {
      return JSON.parse(stored)
    }
  } catch {
    return null
  }
  return null
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(readStoredUser)

  async function login(email, password) {
    const data = await postJson('/login', { email, password })
    setToken(data.access_token)
    sessionStorage.setItem(USER_KEY, JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  function logout() {
    clearToken()
    sessionStorage.removeItem(USER_KEY)
    setUser(null)
  }

  function updateMustChangePassword(value = false) {
    setUser((prev) => {
      if (!prev) return prev
      const next = { ...prev, must_change_password: value }
      sessionStorage.setItem(USER_KEY, JSON.stringify(next))
      return next
    })
  }

  const mustChangePassword = user?.must_change_password === true

  const value = {
    user,
    isAuthenticated: user !== null,
    mustChangePassword,
    login,
    logout,
    updateMustChangePassword,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return context
}