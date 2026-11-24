import { request } from './http'

export const getMyBalance = () => request('/balance/me')