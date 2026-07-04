import { defineStore } from 'pinia'
import api from '@/services/api'

const CACHE_KEY = 'offline_session_cache'
const DEFAULT_OFFLINE_GRACE_DAYS = 14
const MAX_OFFLINE_GRACE_DAYS = 365

function isTokenExpired(token) {
  if (!token) return true
  try {
    const payloadPart = token.split('.')[1]
    if (!payloadPart) return true
    const base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
    const normalized = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
    const payload = JSON.parse(atob(normalized))
    if (!payload.exp) return false
    return Date.now() >= payload.exp * 1000
  } catch {
    return true
  }
}

/**
 * Hash a value with SHA-256 via WebCrypto when available.
 * Returns a hex string. Returns a deterministic fallback only when crypto.subtle
 * is missing (e.g. insecure contexts / older test environments); the fallback
 * is NOT a security guarantee — it merely prevents crashes. The backend remains
 * the authority: the hash is only used to invalidate caches after the user
 * changes their password.
 */
export async function hashSecret(value) {
  if (!value) return null
  const subtle = globalThis.crypto?.subtle
  if (!subtle) {
    let h = 0
    for (let i = 0; i < value.length; i++) {
      h = ((h << 5) - h + value.charCodeAt(i)) | 0
    }
    return `fallback_${value.length}_${h.toString(16)}`
  }
  const buf = await subtle.digest('SHA-256', new TextEncoder().encode(value))
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

export function readOfflineGracePeriodDays() {
  const raw = import.meta.env?.VITE_OFFLINE_GRACE_DAYS
  const parsed = Number(raw)
  if (Number.isFinite(parsed) && parsed > 0 && parsed <= MAX_OFFLINE_GRACE_DAYS) {
    return parsed
  }
  return DEFAULT_OFFLINE_GRACE_DAYS
}

export function readOfflineSessionCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed?.user || !parsed?.passwordHash || !parsed?.cachedAt) return null
    return parsed
  } catch {
    return null
  }
}

function writeOfflineSessionCache(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data))
  } catch {
    /* quota exceeded or storage disabled — ignore, offline cache is best-effort */
  }
}

export function clearOfflineSessionCache() {
  try {
    localStorage.removeItem(CACHE_KEY)
  } catch {
    /* ignore */
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    cachedSession: readOfflineSessionCache(),
    offlineMode: false,
    loading: false,
    syncing: false,
    error: null,
    initMode: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !isTokenExpired(state.token),
    isAuthenticatedOffline: (state) =>
      state.offlineMode && !!state.user && !!state.cachedSession,
    userName: (state) => state.user?.nombre || '',
    isAdmin: (state) => state.user?.is_admin === 1,
  },

  actions: {
    async login(dni, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/api/auth/login', { dni, password })
        this.token = data.access_token
        this.user = data.user
        this.offlineMode = false
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
        await this.cacheSession(password)
        return true
      } catch (err) {
        if (err.response?.status === 401) {
          this.error = 'DNI o contraseña incorrectos'
        } else {
          this.error = 'Error de conexión con el servidor'
        }
        return false
      } finally {
        this.loading = false
      }
    },

    async sincronizar() {
      this.syncing = true
      this.error = null
      try {
        const { data } = await api.post('/api/auth/sincronizar')
        return { ok: true, data }
      } catch (err) {
        this.error = 'No se pudo sincronizar con el servidor'
        return { ok: false }
      } finally {
        this.syncing = false
      }
    },

    async cacheSession(password) {
      if (!this.user || !password) return
      const passwordHash = await hashSecret(password)
      if (!passwordHash) return
      const cachedAt = Date.now()
      this.cachedSession = {
        user: { ...this.user },
        passwordHash,
        cachedAt,
      }
      writeOfflineSessionCache(this.cachedSession)
    },

    isOfflineCacheValid() {
      if (!this.cachedSession?.cachedAt) return false
      const graceDays = readOfflineGracePeriodDays()
      const graceMs = graceDays * 24 * 60 * 60 * 1000
      const age = Date.now() - this.cachedSession.cachedAt
      return age < graceMs
    },

    offlineCacheAgeDays() {
      if (!this.cachedSession?.cachedAt) return null
      const ageMs = Date.now() - this.cachedSession.cachedAt
      return Math.floor(ageMs / (24 * 60 * 60 * 1000))
    },

    async restoreCachedSession() {
      if (!this.cachedSession || !this.isOfflineCacheValid()) return false
      this.user = { ...this.cachedSession.user }
      this.offlineMode = true
      this.initMode = 'offline'
      return true
    },

    logout() {
      this.token = null
      this.user = null
      this.offlineMode = false
      this.initMode = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
      // Keep the offline session cache so the operator can come back without
      // typing credentials while inside the grace period. Clear it explicitly
      // via clearOfflineSessionCache() when the operator really wants to forget
      // the device (e.g. reset / lost device flow).
    },

    clearOfflineCache() {
      clearOfflineSessionCache()
      this.cachedSession = null
    },

    /**
     * Decide how to boot auth at app start.
     *  - mode 'online'         → token vigente contra backend
     *  - mode 'offline'        → sin red, operador entra con cache dentro de la gracia
     *  - mode 'login-required' → con red pero token vencido/ausente → mostrar /login
     *  - mode 'offline-locked' → sin red y cache fuera de gracia → mostrar /login
     */
    initAuth() {
      // Reset previous offline state at boot; restored below if applicable.
      this.offlineMode = false

      if (this.token && !isTokenExpired(this.token)) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        this.initMode = 'online'
        return this.initMode
      }

      const online =
        typeof navigator !== 'undefined' ? navigator.onLine !== false : true

      if (!online) {
        const cached = readOfflineSessionCache()
        this.cachedSession = cached
        if (this.isOfflineCacheValid()) {
          this.user = { ...cached.user }
          this.offlineMode = true
          this.initMode = 'offline'
        } else {
          this.initMode = 'offline-locked'
        }
        return this.initMode
      }

      this.logout()
      this.initMode = 'login-required'
      return this.initMode
    },
  },
})
