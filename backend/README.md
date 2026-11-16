# Pluxee Backend

API REST con **Node.js + Express** (JavaScript, ES Modules).

## Estructura

```
backend/
├── src/
│   ├── config/          ← configuración y variables de entorno
│   ├── routes/          ← definición de endpoints (/api/...)
│   ├── controllers/     ← manejo de req/res
│   ├── services/        ← lógica de negocio
│   ├── models/          ← esquemas / acceso a datos
│   ├── middleware/      ← errorHandler, notFound, auth...
│   ├── utils/           ← helpers
│   ├── app.js           ← instancia de Express (middlewares + rutas)
│   └── server.js        ← arranque del servidor
├── .env.example         ← plantilla de variables de entorno
└── package.json
```

## Puesta en marcha

```bash
cd backend
npm install
copy .env.example .env   # Windows (en Linux/macOS: cp .env.example .env)
npm run dev              # arranca con nodemon en http://localhost:4000
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Estado del servidor |

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PORT` | Puerto del servidor | `4000` |
| `NODE_ENV` | Entorno | `development` |
