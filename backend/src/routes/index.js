import { Router } from 'express'
import { healthRouter } from './health.js'

export const routes = Router()

// Monta las rutas: /api/health
routes.use('/health', healthRouter)
