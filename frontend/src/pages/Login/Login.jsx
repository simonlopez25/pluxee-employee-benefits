import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../../services/http'
import { useAuth } from '../../context/AuthContext'
import './Login.css'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login, user } = useAuth()
  const navigate = useNavigate()

   useEffect(() => {
    if (user) {
      navigate(user.role === 'ADMIN' ? '/dashboard' : '/empleado', { replace: true })
    }
  }, [user, navigate]) 

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)
    try {
      await login(email, password)
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorMessage(error.message)
      } else {
        setErrorMessage('No se ha podido conectar con el servidor')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="loginPage">
      <div className="loginCard">
        <p className="loginBrand">pluxee. benefits</p>
        <h1 className="loginTitle">Iniciar sesión</h1>
        <form className="loginForm" onSubmit={handleSubmit}>
          <label htmlFor="email">Correo electrónico</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          {errorMessage && <p className="loginError">{errorMessage}</p>}
          <button className="loginButton" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Entrando…' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login