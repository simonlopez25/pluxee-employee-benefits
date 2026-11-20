# Pluxee Backend

API REST con **Python + FastAPI** y **PostgreSQL** (SQLAlchemy 2.0).

## Estructura

```
backend/
├── app/
│   ├── main.py                ← instancia FastAPI (middlewares + rutas + handlers)
│   ├── server.py              ← arranque del servidor (uvicorn)
│   ├── core/                  ← infraestructura transversal
│   │   ├── config.py          ← variables de entorno (pydantic-settings + .env)
│   │   ├── database.py        ← engine + sesión PostgreSQL (SQLAlchemy 2.0)
│   │   └── errors.py          ← AppError (errores con código HTTP)
│   ├── routes/                ← definición de endpoints (/api/...)
│   ├── schemas/               ← validación de entrada/salida (Pydantic)
│   ├── services/              ← lógica de negocio
│   └── models/                ← 13 modelos SQLAlchemy (una tabla por archivo)
│       ├── __init__.py            ← importa los 13 (requisito del autogenerate)
│       ├── department.py          ├── global_budget.py
│       ├── user.py                ├── benefit.py
│       ├── package.py             ├── package_benefit.py
│       ├── department_budget.py   ├── employee_assignment.py
│       ├── expense.py             ├── expense_allocation.py
│       ├── expense_history.py     └── audit_log.py
│       └── attachment.py
├── alembic/                   ← migraciones (Alembic)
│   ├── env.py                     ← conecta Alembic con .env y Base.metadata
│   └── versions/                  ← archivos de migración generados
├── alembic.ini                ← configuración de Alembic
├── seed.sql                   ← datos de prueba (ver «Datos de prueba»)
├── scripts/
│   └── seed.py                    ← runner del seed (npm run seed [--reset])
├── tests/                     ← tests con pytest
├── .env.example               ← plantilla de variables de entorno
├── pytest.ini                 ← configuración de pytest
└── requirements.txt           ← dependencias (pip)
```

## Flujo de una petición

```
routes → schema (Pydantic) → service → model (SQL) → PostgreSQL
   │            │               │            │
   │            │               │            └─ queries SQL con SQLAlchemy
   │            │               └─ lógica de negocio
   │            └─ validación/serialización de la respuesta
   └─ endpoint (FastAPI) + inyección de sesión con get_db
```

Errores centralizados: los services lanzan `AppError` (ver `app/core/errors.py`) y
`app/main.py` los convierte en respuesta JSON con su código HTTP.

## Puesta en marcha

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Linux/macOS: .venv/bin/pip install -r requirements.txt
copy .env.example .env                          # Linux/macOS: cp .env.example .env
# Edita .env con tus datos de PostgreSQL
.venv\Scripts\python -m uvicorn app.main:app --reload   # → http://localhost:4000 (docs: /docs)
```

## Tests

```bash
cd backend
.venv\Scripts\python -m pytest   # Linux/macOS: .venv/bin/python -m pytest
```

## Migraciones (Alembic)

El esquema de la BD se gestiona con **Alembic**. La URL y los modelos se
cargan desde `app/core/config.py` y `app/core/database.py` (ver `alembic/env.py`);
**no** editar `sqlalchemy.url` en `alembic.ini`.

```bash
cd backend

# 1. Editas/agregas modelos en app/models/ (heredan de Base)
# 2. Generar la revisión (compara contra la BD actual):
.venv\Scripts\python -m alembic revision --autogenerate -m "descripcion del cambio"

# 3. Revisar el archivo generado en alembic/versions/ y aplicar:
.venv\Scripts\python -m alembic upgrade head

# Comandos útiles
.venv\Scripts\python -m alembic current     # versión aplicada a la BD
.venv\Scripts\python -m alembic history     # todas las revisiones
.venv\Scripts\python -m alembic downgrade base   # retroceder todo (¡cuidado!)
```

> El autogenerate solo detecta cambios en modelos importados desde
> `app.core.database.Base` — si agregas un modelo nuevo, impórtalo en
> `app/models/__init__.py` para que lo incluya.

## Tablas (esquema)

13 tablas (el DDL completo está en `alembic/versions/`: baseline
`4957b7117a5c` + `5f2c8a91e4d7`):

| Grupo | Tablas |
|-------|--------|
| Estructura | `departments`, `users` |
| Catálogos | `benefits`, `packages`, `package_benefits` |
| Presupuestos | `global_budgets`, `department_budgets` |
| Asignaciones | `employee_assignments` |
| Transaccional | `expenses`, `expense_allocations`, `attachments` |
| Auditoría | `expense_history`, `audit_logs` |

Relación paquete ↔ grupo de empleados (departamento): **N paquetes por
grupo, un grupo por paquete** — `packages.department_id NOT NULL`. Si dos
grupos necesitan la misma asignación, se crean dos paquetes distintos. El
presupuesto con el que se cruzan se deriva:
`departments → department_budgets(department_id) → global_budgets(period)`.

Los constraints (CHECK, FK, UNIQUE) están declarados **con sus nombres
exactos** en los modelos (`app/models/`) y en las migraciones — `alembic
revision --autogenerate` contra una BD al día debe quedar **vacío**.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servidor y de PostgreSQL |
| GET | `/docs` | Documentación OpenAPI (Swagger) |

## Datos de prueba (seed)

`seed.sql` trae datos inventados (3 departamentos, 7 usuarios, presupuestos de
noviembre de 2026, gastos y justificantes de ejemplo) para desarrollo y demo —
**nunca** para producción. Contraseña de prueba de todos los usuarios:
`Prueba123!`.

```bash
# Desde la raíz del repo — usa la conexión de la app (Neon o local)
npm run seed              # si la BD está vacía
npm run seed -- --reset   # TRUNCATE de las 13 tablas y vuelve a sembrar
```

En **pgAdmin** (Postgres local migrada con `alembic upgrade head`): pega
`seed.sql` en el Query Tool y ejecuta con F5. La comprobación final debe dar
a Lucía **Comida = 70,00** y **Transporte = 10,00** (el runner imprime
`SEED RESULT: PASS`).

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PORT` | Puerto del servidor | `4000` |
| `APP_ENV` | Entorno (`development` \| `production` \| `test`) | `development` |
| `CORS_ORIGINS` | Orígenes CORS permitidos (separados por coma) | `http://localhost:5173` |
| `DB_HOST` | Host de PostgreSQL (fallback local) | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL (fallback local) | `5432` |
| `DB_USER` | Usuario de PostgreSQL (fallback local) | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL (fallback local) | `` |
| `DB_NAME` | Base de datos (fallback local) | `pluxee` |
| `DATABASE_URL` | URL completa de Neon para la app (pooled); si falta, se lee de `../.env.local` en la raíz | `` |
| `DATABASE_URL_UNPOOLED` | URL directa de Neon para Alembic (sin pooler); si falta, se usa `DATABASE_URL` | `` |

> La BD compartida del equipo vive en **Neon**: `neon env pull` escribe
> `../.env.local` en la raíz y la app la detecta sin tocar `backend/.env`
> (ver [README principal](../README.md#base-de-datos-compartida-neon)).
> Si no hay ninguna `DATABASE_URL`, se usa la Postgres local (`DB_*`).
