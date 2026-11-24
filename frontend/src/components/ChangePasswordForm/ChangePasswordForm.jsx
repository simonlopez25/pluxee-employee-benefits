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
  const [successMessage, setSuccessMessage] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setErrorMessage('')
    setSuccessMessage('')

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
      setSuccessMessage('Contraseña actualizada correctamente')
      updateMustChangePassword(false)
      if (onSuccess) onSuccess()
    } catch (err) {
      setErrorMessage(err?.message || 'Error inesperado')
    } finally {
      setIsSubmitting(false)
    }
  }

  const card = (
    <div className="changePasswordCard">
      <p className="changePasswordBrand">pluxee. benefits</p>
      <h1 className="changePasswordTitle">
        {isForced ? 'Cambio de contraseña obligatorio' : 'Cambiar contraseña'}
      </h1>
      <form className="changePasswordForm" onSubmit={handleSubmit}>
        <label htmlFor="currentPassword">Contraseña actual</label>
        <input
          id="currentPassword"
          className="changePasswordInput"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
        />
        <label htmlFor="newPassword">Nueva contraseña</label>
        <input
          id="newPassword"
          className="changePasswordInput"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        <label htmlFor="confirmPassword">Confirmar nueva contraseña</label>
        <input
          id="confirmPassword"
          className="changePasswordInput"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        {errorMessage && <p className="changePasswordError">{errorMessage}</p>}
        {successMessage && <p className="changePasswordSuccess">{successMessage}</p>}
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

  if (isForced) {
    return <div className="changePasswordPage">{card}</div>
  }
  return card
}

export default ChangePasswordForm
