import axios from 'axios'
import { useToastStore } from '@/stores/toast'

let onUnauthorized = null

export function normalizeBaseURL(value) {
  const baseURL = value || 'http://localhost:8000'
  return baseURL.replace(/\/api\/?$/, '')
}

const api = axios.create({
  baseURL: normalizeBaseURL(import.meta.env.VITE_API_URL),
  headers: { 'Content-Type': 'application/json' }
})

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const requestUrl = error?.config?.url || ''
    const isAuthLogin = requestUrl.includes('/api/auth/login')

    if (status === 401 && !isAuthLogin) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common.Authorization
      if (typeof onUnauthorized === 'function') {
        onUnauthorized()
      }
    }

    if (!error.response) {
      useToastStore().error('Backend no disponible', 'No se pudo conectar con el servidor.')
    } else if (status === 403) {
      useToastStore().error('Acceso restringido', error.response?.data?.detail || 'No tenes permisos para esta accion.')
    } else if (status >= 500) {
      useToastStore().error('Error del servidor', error.response?.data?.detail || 'Intenta nuevamente en unos minutos.')
    }

    return Promise.reject(error)
  }
)

export default api
