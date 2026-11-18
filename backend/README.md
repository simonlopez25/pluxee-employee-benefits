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
│   └── models/                ← queries SQL / acceso a datos
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
