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
│   └── models/                ← 14 modelos SQLAlchemy (una tabla por archivo)
│       ├── __init__.py            ← importa los 14 (requisito del autogenerate)
│       ├── department.py          ├── global_budget.py
│       ├── user.py                ├── benefit.py
│       ├── package.py             ├── package_benefit.py
│       ├── department_budget.py   ├── department_assignment.py
│       ├── employee_assignment.py ├── expense.py
│       ├── expense_allocation.py  ├── attachment.py
│       ├── expense_history.py     └── audit_log.py
├── alembic/                   ← migraciones (Alembic)
│   ├── env.py                     ← conecta Alembic con .env y Base.metadata
│   └── versions/                  ← archivos de migración generados
├── alembic.ini                ← configuración de Alembic
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

14 tablas (ver el DDL completo en la migración baseline `alembic/versions/*_initial_schema.py`):

| Grupo | Tablas |
|-------|--------|
| Estructura | `departments`, `users` |
| Catálogos | `benefits`, `packages`, `package_benefits` |
| Presupuestos | `global_budgets`, `department_budgets` |
| Asignaciones | `department_assignments`, `employee_assignments` |
| Transaccional | `expenses`, `expense_allocations`, `attachments` |
| Auditoría | `expense_history`, `audit_logs` |

Los constraints (CHECK, FK compuestas, UNIQUE) están declarados **con sus nombres
exactos** en los modelos (`app/models/`) y en la migración baseline — `alembic
revision --autogenerate` contra una BD al día debe quedar **vacío**.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servidor y de PostgreSQL |
| GET | `/docs` | Documentación OpenAPI (Swagger) |

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PORT` | Puerto del servidor | `4000` |
| `APP_ENV` | Entorno (`development` \| `production` \| `test`) | `development` |
| `CORS_ORIGINS` | Orígenes CORS permitidos (separados por coma) | `http://localhost:5173` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `` |
| `DB_NAME` | Base de datos | `pluxee` |
