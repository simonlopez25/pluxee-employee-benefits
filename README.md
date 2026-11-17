# Pluxee Employee Benefits

Monorepo con el frontend y el backend de la aplicación de beneficios para empleados.

## Estructura

```
pluxee-employee-benefits/
├── frontend/          ← React 19 + Vite (JavaScript)
│   └── src/
│       ├── components/    ← Atomic Design (atoms, molecules, organisms, templates)
│       ├── pages/         ← páginas de la app
│       ├── hooks/         ← hooks personalizados
│       ├── services/      ← cliente de la API
│       ├── styles/        ← estilos globales
│       └── assets/        ← imágenes y estáticos
├── backend/           ← Node.js + Express (API REST)
│   └── src/
│       ├── app/            ← arranque y instancia de Express
│       │   ├── app.js          ← instancia Express + middlewares + rutas
│       │   └── server.js       ← arranque del servidor (listen)
│       ├── core/          ← infraestructura transversal
│       │   ├── config/        ← variables de entorno
│       │   ├── db/            ← pool de conexión PostgreSQL
│       │   ├── errors/        ← AppError y errores centralizados
│       │   └── middleware/    ← errorHandler, validate, auth...
│       ├── routes/        ← endpoints (capa api)
│       ├── controllers/   ← manejo de req/res (delgados)
│       ├── services/      ← lógica de negocio
│       ├── schemas/       ← validación de entrada/salida (zod)
│       └── models/        ← queries SQL / acceso a datos
├── package.json       ← scripts de conveniencia
└── README.md
```

Flujo de una petición:

```
routes → validate(schema) → controller → service → model (SQL) → PostgreSQL
```

## Requisitos

- Node.js 18+
- npm
- PostgreSQL (opcional para desarrollo: solo necesario al consultar la BD)

## Puesta en marcha

```bash
# 1. Instalar dependencias
npm install --prefix frontend
npm install --prefix backend

# 2. Configurar el backend (variables de entorno)
copy backend\.env.example backend\.env   # Linux/macOS: cp backend/.env.example backend/.env

# 3. Arrancar (cada servicio en su terminal)
npm run dev        # frontend → http://localhost:5173
npm run dev:api    # backend  → http://localhost:4000
```

El frontend tiene configurado un **proxy** en `vite.config.js`: las llamadas a `/api/*` se redirigen al backend en el puerto `4000`.

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Arranca el frontend (Vite) |
| `npm run dev:api` | Arranca el backend (nodemon) |
| `npm run build` | Build de producción del frontend |
| `npm run lint` | Lint del frontend (ESLint) |
| `npm run start:api` | Arranca el backend en producción |

## Metodología UI

Los componentes siguen **Atomic Design** — ver [frontend/src/components/README.md](frontend/src/components/README.md).
