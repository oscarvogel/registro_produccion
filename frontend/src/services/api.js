import axios from 'axios'
import { useToastStore } from '@/stores/toast'
import { useConnectivityStore } from '@/stores/connectivity'

let onUnauthorized = null
export const SERVER_ERROR_MESSAGE = 'No se pudo conectar con el servidor. Intenta nuevamente en unos minutos.'

export function normalizeBaseURL(value) {
  const baseURL = value || ''
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
    // Callers can opt-out from the global toast by passing
    // `{ _suppressErrorToast: true }` on the request config (used by the
    // login flow to render its own contextual message instead of a generic
    // toast).
    const suppressToast = error?.config?._suppressErrorToast === true

    if (status === 401 && !isAuthLogin) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common.Authorization
      if (typeof onUnauthorized === 'function') {
        onUnauthorized()
      }
    }

    if (suppressToast) {
      return Promise.reject(error)
    }

    // When the operator is already offline, the global amber banner is
    // telling them the same story — showing an additional error toast for
    // every API request that fails because of the missing connection is just
    // noise. We only suppress "no response" errors here (and 5xx sentinels);
    // permission / 401 / 4xx feedback still surfaces even while offline.
    const knownOffline = (() => {
      try {
        return useConnectivityStore().isOffline === true
      } catch {
        return false
      }
    })()

    const noResponse = !error.response

    if (noResponse && knownOffline) {
      // The amber offline banner has it covered — stay silent.
      return Promise.reject(error)
    }

    if (noResponse) {
      useToastStore().error('Backend no disponible', 'No se pudo conectar con el servidor.')
    } else if (status === 403) {
      useToastStore().error('Acceso restringido', error.response?.data?.detail || 'No tenes permisos para esta accion.')
    } else if (status >= 500) {
      // 5xx never leaks backend detail to the UI; only the generic message.
      useToastStore().error('Error del servidor', SERVER_ERROR_MESSAGE)
    } else if (status === 401 && !isAuthLogin) {
      useToastStore().error('Sesion expirada', 'Volvé a iniciar sesion para continuar.')
    }

    return Promise.reject(error)
  }
)

export default api
