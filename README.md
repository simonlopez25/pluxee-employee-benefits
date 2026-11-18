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
├── backend/           ← Python + FastAPI (API REST)
│   └── app/
│       ├── main.py          ← instancia FastAPI + middlewares + handlers
│       ├── server.py        ← arranque del servidor (uvicorn)
│       ├── core/            ← infraestructura transversal
│       │   ├── config.py        ← variables de entorno (pydantic-settings)
│       │   ├── database.py      ← engine + sesión PostgreSQL (SQLAlchemy 2.0)
│       │   └── errors.py        ← AppError y errores centralizados
│       ├── routes/          ← endpoints (capa API)
│       ├── schemas/         ← validación de entrada/salida (Pydantic)
│       ├── services/        ← lógica de negocio
│       └── models/          ← queries SQL / acceso a datos
├── package.json       ← scripts de conveniencia
└── README.md
```

Flujo de una petición:

```
routes → schema (Pydantic) → service → model (SQL) → PostgreSQL
```

## Requisitos

- Python 3.11+ (probado con 3.14)
- npm (solo para el frontend)
- PostgreSQL (opcional para desarrollo: solo necesario al consultar la BD)

## Puesta en marcha

```bash
# 1. Frontend
npm install --prefix frontend

# 2. Backend: entorno virtual + dependencias
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Linux/macOS: .venv/bin/pip install -r requirements.txt
copy .env.example .env                          # Linux/macOS: cp .env.example .env
cd ..

# 3. Arrancar (cada servicio en su terminal)
npm run dev        # frontend → http://localhost:5173
npm run dev:api    # backend  → http://localhost:4000  (docs en /docs)
```

El frontend tiene configurado un **proxy** en `vite.config.js`: las llamadas a `/api/*` se redirigen al backend en el puerto `4000`.

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Arranca el frontend (Vite) |
| `npm run dev:api` | Arranca el backend (uvicorn con reload) |
| `npm run build` | Build de producción del frontend |
| `npm run lint` | Lint del frontend (ESLint) |
| `npm run start:api` | Arranca el backend en producción |

Tests del backend:

```bash
cd backend
.venv\Scripts\python -m pytest   # Linux/macOS: .venv/bin/python -m pytest
```

Al agregar una dependencia nueva al backend:

```bash
cd backend
.venv\Scripts\pip install <paquete>
.venv\Scripts\pip freeze > requirements.txt
```

## Metodología UI

Los componentes siguen **Atomic Design** — ver [frontend/src/components/README.md](frontend/src/components/README.md).
