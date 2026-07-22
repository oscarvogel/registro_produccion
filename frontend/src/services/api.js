import axios from 'axios'
import { useToastStore } from '@/stores/toast'
import { useConnectivityStore } from '@/stores/connectivity'

let onUnauthorized = null
export const SERVER_ERROR_MESSAGE = 'No se pudo conectar con el servidor. Intenta nuevamente en unos minutos.'
const TECHNICAL_ERROR_PATTERN = /sql|mysql|pymysql|sqlalchemy|operationalerror|integrityerror|programmingerror|databaseerror|traceback|select\s+|insert\s+|update\s+|delete\s+|from\s+[`"\w]+|where\s+|password_hash|usuarios/i

export function normalizeBaseURL(value) {
  const baseURL = value || ''
  return baseURL.replace(/\/api\/?$/, '')
}

export function isUnsafeErrorDetail(detail) {
  return typeof detail === 'string' && TECHNICAL_ERROR_PATTERN.test(detail)
}

export function getUserSafeErrorMessage(error, fallback = SERVER_ERROR_MESSAGE) {
  const status = error?.response?.status
  const detail = error?.response?.data?.detail
  if (status >= 500 || isUnsafeErrorDetail(detail)) {
    return fallback
  }
  return detail || fallback
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

    // When the operator is already offline (or the backend healthcheck is
    // degraded), the global banner is telling them the same story — showing
    // an additional "no response" toast for every failing request is just
    // noise. We also fall back to `navigator.onLine === false` directly to
    // close the race window between losing the network and the next periodic
    // healthcheck flipping isBackendUp.
    const knownDown = (() => {
      try {
        if (useConnectivityStore().isOfflineOrBackendDown === true) return true
      } catch {
        /* ignore */
      }
      if (typeof navigator !== 'undefined' && navigator.onLine === false) return true
      return false
    })()

    const noResponse = !error.response

    if (noResponse && knownDown) {
      // The banner has it covered — stay silent.
      return Promise.reject(error)
    }

    if (noResponse) {
      useToastStore().error('Backend no disponible', 'No se pudo conectar con el servidor.')
    } else if (status === 403) {
      useToastStore().error('Acceso restringido', getUserSafeErrorMessage(error, 'No tenes permisos para esta accion.'))
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
