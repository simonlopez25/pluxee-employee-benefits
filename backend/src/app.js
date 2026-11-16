import express from 'express'
import cors from 'cors'
import { routes } from './routes/index.js'
import { notFound, errorHandler } from './middleware/errorHandler.js'

export const app = express()

// Middlewares globales
app.use(cors())
app.use(express.json())

// Rutas de la API (prefijo /api)
app.use('/api', routes)

// 404 y manejo de errores (siempre al final)
app.use(notFound)
app.use(errorHandler)
