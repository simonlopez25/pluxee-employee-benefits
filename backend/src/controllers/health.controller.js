import { config } from '../config/index.js'

// GET /api/health — comprobación de que el servidor está vivo
export function healthCheck(req, res) {
  res.status(200).json({
    status: 'ok',
    service: 'pluxee-backend',
    env: config.nodeEnv,
    timestamp: new Date().toISOString(),
  })
}
