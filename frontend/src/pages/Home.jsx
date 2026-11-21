import { useAuth } from '../context/AuthContext'
import '../styles/Home.css'

function Home() {
  const { user, logout } = useAuth()

  return (
    <div className="homePage">
      <div className="homeCard">
        <span className="homeRole">
          {user.role === 'ADMIN' ? 'Administrador' : 'Empleado'}
        </span>
        <h1 className="homeTitle">Hola, {user.full_name}</h1>
        <p className="homeEmail">{user.email}</p>
        <button className="homeButton" type="button" onClick={logout}>
          Cerrar sesión
        </button>
      </div>
    </div>
  )
}

export default Home