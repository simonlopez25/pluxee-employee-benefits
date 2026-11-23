import ChangePasswordForm from '../components/ChangePasswordForm/ChangePasswordForm'

function Profile() {
  return (
    <div>
      <h1>Mi perfil</h1>
      <ChangePasswordForm isForced={false} />
    </div>
  )
}

export default Profile
