import { useState } from 'react'
import { patchJson } from '../../services/http'
import { useAuth } from '../../context/AuthContext'
import './changePasswordForm.css'

function ChangePasswordForm({ isForced = false, onSuccess }) {
  const { updateMustChangePassword } = useAuth()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')

    if (newPassword !== confirmPassword) {
      setErrorMessage('La nueva contraseña y su confirmación no coinciden')
      return
    }
    if (newPassword.length < 10) {
      setErrorMessage('La nueva contraseña debe tener al menos 10 caracteres')
      return
    }
    if (newPassword === currentPassword) {
      setErrorMessage('La nueva contraseña debe ser diferente a la actual')
      return
    }

    setIsSubmitting(true)
    try {
      await patchJson('/users/me/password', {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      updateMustChangePassword(false)
      if (onSuccess) onSuccess()
    } catch (err) {
      setErrorMessage(err?.message || 'Error inesperado')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="changePasswordCard">
      <h2 className="changePasswordTitle">
        {isForced ? 'Cambio de contraseña obligatorio' : 'Cambiar contraseña'}
      </h2>
      <form className="changePasswordForm" onSubmit={handleSubmit}>
        <label className="changePasswordLabel">
          Contraseña actual
          <input
            className="changePasswordInput"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
          />
        </label>
        <label className="changePasswordLabel">
          Nueva contraseña
          <input
            className="changePasswordInput"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
        </label>
        <label className="changePasswordLabel">
          Confirmar nueva contraseña
          <input
            className="changePasswordInput"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </label>
        {errorMessage && (
          <p className="changePasswordError">{errorMessage}</p>
        )}
        <button
          className="changePasswordButton"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Guardando...' : 'Cambiar contraseña'}
        </button>
      </form>
    </div>
  )
}

export default ChangePasswordForm
