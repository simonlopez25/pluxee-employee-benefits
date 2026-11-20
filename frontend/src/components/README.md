# Componentes — Atomic Design

Estructura de UI basada en la metodología [Atomic Design](https://atomicdesign.bradfrost.com/) de Brad Frost, organizada en carpetas modulares por componente.

## Organización por Carpetas

Cada componente se aloja en su propia carpeta que agrupa su lógica JSX, sus estilos CSS dedicados y un archivo barril `index.js` para simplificar importaciones:

```
components/
├── atoms/
│   ├── Badge/
│   │   ├── Badge.jsx
│   │   ├── Badge.css
│   │   └── index.js
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.css
│   │   └── index.js
│   └── Icon/
│       ├── Icon.jsx
│       ├── Icon.css
│       └── index.js
├── molecules/
│   ├── BenefitCard/
│   │   ├── BenefitCard.jsx
│   │   ├── BenefitCard.css
│   │   └── index.js
│   └── FilterTabs/
│       ├── FilterTabs.jsx
│       ├── FilterTabs.css
│       └── index.js
├── organisms/
│   ├── AdminSidebar/
│   │   ├── AdminSidebar.jsx
│   │   ├── AdminSidebar.css
│   │   └── index.js
│   ├── BenefitFormModal/
│   │   ├── BenefitFormModal.jsx
│   │   ├── BenefitFormModal.css
│   │   └── index.js
│   └── BenefitsCatalogSection/
│       ├── BenefitsCatalogSection.jsx
│       ├── BenefitsCatalogSection.css
│       └── index.js
└── templates/
    └── AdminLayout/
        ├── AdminLayout.jsx
        ├── AdminLayout.css
        └── index.js
```

## Niveles

| Nivel | Carpeta | Descripción | Componentes actuales |
|---|---|---|---|
| **Atoms** | `atoms/` | Bloques indivisibles sin dependencias internas. | `Badge`, `Button`, `Icon` |
| **Molecules** | `molecules/` | Combinación simple de átomos con un propósito visual concreto. | `BenefitCard`, `FilterTabs` |
| **Organisms** | `organisms/` | Secciones complejas con interacción y lógica de estado. | `AdminSidebar`, `BenefitFormModal`, `BenefitsCatalogSection` |
| **Templates** | `templates/` | Layouts estructurales sin datos de negocio. | `AdminLayout` |
| **Pages** | `pages/` | Páginas enlazadas al router que orquestan datos y secciones. | `BenefitsCatalogPage`, `PlaceholderPage` |

## Reglas

1. **Separación estricta de JSX y CSS:** Cada componente tiene su archivo `.jsx` y su archivo `.css` separado sin estilos en línea.
2. **Nomenclatura:** Clases CSS, variables y funciones en `camelCase`. Componentes en `PascalCase`. Identificadores en inglés y textos visibles al usuario en español.
3. **Jerarquía:** Los átomos no importan otros componentes. Las moléculas solo importan átomos. Los organismos importan moléculas y átomos. Las páginas orquestan organismos y servicios API.
