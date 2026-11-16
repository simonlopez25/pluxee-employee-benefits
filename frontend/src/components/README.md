# Componentes — Atomic Design

Estructura de UI basada en la metodología [Atomic Design](https://atomicdesign.bradfrost.com/) de Brad Frost.

## Niveles

| Nivel | Carpeta | Descripción | Ejemplo |
|-------|---------|-------------|---------|
| **Atoms** | `atoms/` | Bloques más pequeños e indivisibles. No tienen dependencias internas. | `Button`, `Input`, `Badge`, `Icon`, `Typography` |
| **Molecules** | `molecules/` | Combinación simple de 2+ átomos con un propósito concreto. | `SearchBar` (Input + Button), `BenefitCard` (Badge + Title + Text) |
| **Organisms** | `organisms/` | Secciones complejas compuestas por moléculas y/o átomos. | `Header`, `Footer`, `BenefitList`, `HeroSection` |
| **Templates** | `templates/` | Layouts de página sin contenido real, solo la estructura. | `MainLayout`, `AuthLayout` |

## Reglas

1. **Los átomos no importan de otros componentes**, solo de `styles/` o `assets/`.
2. **Las moléculas solo importan átomos**; los organismos, moléculas y átomos.
3. **Las plantillas solo componen organismos**; nunca contienen datos de negocio.
4. **Las páginas** (en `../pages/`) viven fuera de `components/` y sí manejan datos y estado.
5. Cada componente en su propio archivo: `Button.jsx` → exporta `Button` (named o default, consistente en todo el proyecto).

## Ejemplo de uso

```jsx
// components/atoms/Button.jsx
export function Button({ children, onClick }) {
  return <button onClick={onClick}>{children}</button>
}

// pages/Home.jsx
import { Button } from '../components/atoms/Button'

export function Home() {
  return <Button onClick={() => {}}>Hola</Button>
}
```
