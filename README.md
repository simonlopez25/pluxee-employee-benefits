<img width="2172" height="724" alt="Plataforma Pluxee de beneficios laborales" src="https://github.com/user-attachments/assets/fcad27ef-6ff8-46df-88c8-d176b007d153" />




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
│   └── alembic/           ← migraciones de BD (Alembic)
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
- Cuenta Neon (la BD compartida vive en la nube; ver [Base de datos compartida](#base-de-datos-compartida-neon))

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

## Base de datos compartida (Neon)

La BD es **Postgres 18 en la nube (Neon)**: todos los compañeros trabajan
contra los mismos datos desde su máquina local. La CLI de Neon escribe las
credenciales en `.env.local` (raíz del repo) y `backend/app/core/config.py` la
detecta automáticamente — no hay que copiar nada a mano.

**Proyecto**: `pluxee` (`fancy-glitter-51900277`) · **rama**: `production` ·
**región**: `aws-us-east-2` (Ohio, EE. UU.)

### Puesta en marcha de un compañero

```bash
# 1. CLI de Neon (solo la primera vez; sin npm global usa `npx neon@latest`)
npm i -g neon@latest

# 2. Login en el navegador (sesión propia: nunca compartas la cuenta)
neon login

# 3. Desde la raíz del repo: baja DATABASE_URL a .env.local
neon env pull --project-id fancy-glitter-51900277 --branch production

# 4. Arrancar como siempre
npm run dev        # frontend → http://localhost:5173
npm run dev:api    # backend  → http://localhost:4000 (contra Neon)
```

Comprobación: abre `http://localhost:4000/api/health` →
`{"status":"ok","database":"up"}`.

### Seguridad de las claves

- `.env.local` (raíz) y `backend/.env` están en `.gitignore`: **nunca se suben**
  al repo. No pegues credenciales en código, commits ni chats.
- Cada persona usa su propia sesión (`neon login`). Si prefieres una API key:
  `neon profile create work --api-key <KEY>` — guárdala fuera del repo.
- Para dar de alta a alguien, invítalo desde Neon Console → **Members** en vez
  de enviar la connection string.

### Comportamiento

- Sin `.env.local`, el backend cae a la Postgres local (`DB_*` en
  `backend/.env`) como fallback.
- Las migraciones de **Alembic** usan la conexión directa
  (`DATABASE_URL_UNPOOLED`) automáticamente:
  `cd backend && .venv\Scripts\python -m alembic upgrade head`.
- `neon.ts` define la política de ramas (las ramas no-default expiran a los
  7 días); se aplica con `neon deploy`.

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

Migraciones de base de datos con **Alembic**: ver [backend/README.md](backend/README.md).

## Metodología UI

Los componentes siguen **Atomic Design** — ver [frontend/src/components/README.md](frontend/src/components/README.md).
