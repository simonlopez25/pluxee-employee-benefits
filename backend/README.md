# Pluxee Backend

API REST con **Node.js + Express** (JavaScript, ES Modules) y **PostgreSQL**.

## Estructura

```
backend/
├── src/
│   ├── app/                    ← arranque y instancia de Express
│   │   ├── app.js              ← instancia Express (middlewares + rutas)
│   │   └── server.js           ← arranque del servidor
│   ├── core/                  ← infraestructura transversal
│   │   ├── config/            ← variables de entorno
│   │   ├── db/                ← pool de conexión PostgreSQL (pg)
│   │   ├── errors/            ← AppError (errores con código HTTP)
│   │   └── middleware/        ← errorHandler, notFound, validate...
│   ├── routes/                ← definición de endpoints (/api/...)
│   ├── controllers/           ← manejo de req/res (delgados)
│   ├── services/              ← lógica de negocio
│   ├── schemas/               ← validación de entrada/salida (zod)
│   ├── models/                ← queries SQL / acceso a datos
├── .env.example               ← plantilla de variables de entorno
└── package.json
```

## Flujo de una petición

```
routes → validate(schema) → controller → service → model (SQL) → PostgreSQL
   │                          │            │            │
   │                          │            │            └─ queries SQL con pg
   │                          │            └─ lógica de negocio
   │                          └─ solo req/res, llama al service
   └─ endpoint + validación con zod (core/middleware/validate)
```

Errores centralizados en `core/middleware/errorHandler.js` usando `core/errors/AppError.js`.

## Puesta en marcha

```bash
cd backend
npm install
copy .env.example .env   # Windows (en Linux/macOS: cp .env.example .env)
# Edita .env con tus datos de PostgreSQL
npm run dev              # arranca con nodemon en http://localhost:4000
```

> Nota: los archivos de `src/` están vacíos (plantilla de estructura). Rellenarlos en este orden:
> `core/config` → `core/db` → `core/middleware` → `models` → `schemas` → `services` → `controllers` → `routes` → `app/app.js` → `app/server.js`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servidor |

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PORT` | Puerto del servidor | `4000` |
| `NODE_ENV` | Entorno | `development` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `DB_USER` | Usuario de PostgreSQL | `postgres` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `` |
| `DB_NAME` | Base de datos | `pluxee` |
