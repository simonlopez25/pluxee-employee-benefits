import { Router } from 'express'
import { healthCheck } from '../controllers/health.controller.js'

export const healthRouter = Router()

// GET /api/health
healthRouter.get('/', healthCheck)
