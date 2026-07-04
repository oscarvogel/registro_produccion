import { defineStore } from 'pinia'
import { checkBackend } from '@/services/healthCheck'

const DEFAULT_HEALTHCHECK_INTERVAL_MS = 30 * 1000
const DEFAULT_HEALTHCHECK_TIMEOUT_MS = 3000
const HEALTHCHECK_TTL_MS = 30 * 1000

function readInitialOnline() {
  if (typeof navigator === 'undefined') return true
  return navigator.onLine !== false
}

/**
 * Centralized online / backend state shared across the app.
 *
 * The PWA must show the offline banner from the very first frame, both on
 * `/login` (where the operator lands when the cached session expired) and on
 * any authenticated route. Earlier the banner lived in `App.vue` but only
 * inside the `v-if="authStore.isAuthenticated"` branch, so a first-time
 * operator without network never saw it.
 *
 * This store exposes:
 *   - `isOnline`     → navigator.onLine, refreshed by the
 *                       'online'/'offline' window events.
 *   - `isBackendUp`  → result of GET /api/health (timeout default 3s).
 *                       Refreshed periodically (default 30s) and on demand.
 *                       Survives from a cache (TTL 30s) so we do not hammer
 *                       the endpoint on every view.
 *
 * Call `useConnectivityStore().init()` once from `main.js` so the listeners
 * are registered at boot. After `init()`, `main.js` fires a non-blocking
 * `refreshBackendHealth()` so the UI knows about degraded backends within a
 * few seconds, without delaying first paint.
 */
export const useConnectivityStore = defineStore('connectivity', {
  state: () => ({
    isOnline: readInitialOnline(),
    isBackendUp: readInitialOnline(),
    lastBackendCheckAt: 0,
    lastHealthResult: null,
    pendingInitialHealthCheck: true,
  }),

  getters: {
    isOffline: (state) => state.isOnline === false,
    isBackendDegraded: (state) => state.isOnline !== false && state.isBackendUp === false,
    isOfflineOrBackendDown: (state) =>
      state.isOnline === false || state.isBackendUp === false,
    hasFreshBackendState: (state) => {
      if (!state.lastBackendCheckAt) return false
      return Date.now() - state.lastBackendCheckAt < HEALTHCHECK_TTL_MS
    },
  },

  actions: {
    _setOnline(value) {
      const wasOnline = this.isOnline
      this.isOnline = value
      if (!value) {
        // If we just lost the link to the network, the backend is also down
        // from our perspective until proven otherwise.
        this.isBackendUp = false
      } else if (!wasOnline) {
        // Coming back online does NOT mean the backend is healthy — kick a
        // real healthcheck now so the UI updates within a few seconds.
        this.refreshBackendHealth({ force: true }).catch(() => {
          /* the store already reflects the latest state */
        })
      }
    },

    init() {
      if (typeof window === 'undefined') return
      if (this._initialized) return
      this._initialized = true

      // Sync once before listening.
      this._setOnline(readInitialOnline())

      // Named handlers so we can remove them later (used by the test suite
      // and by app teardown if needed).
      this._handleOnline = () => this._setOnline(true)
      this._handleOffline = () => this._setOnline(false)
      window.addEventListener('online', this._handleOnline)
      window.addEventListener('offline', this._handleOffline)
    },

    teardown() {
      if (typeof window === 'undefined') return
      if (!this._initialized) return
      if (this._handleOnline) {
        window.removeEventListener('online', this._handleOnline)
      }
      if (this._handleOffline) {
        window.removeEventListener('offline', this._handleOffline)
      }
      this.stopPeriodicHealthChecks()
      this._initialized = false
      this._handleOnline = null
      this._handleOffline = null
    },

    /**
     * Hit GET /api/health with a short timeout. Caches the latest known
     * healthy/degraded state for 30s to avoid hammering the endpoint.
     */
    async refreshBackendHealth({ force = false, timeoutMs = DEFAULT_HEALTHCHECK_TIMEOUT_MS } = {}) {
      // Skip when we know we are offline — saves the request.
      if (!this.isOnline) {
        this.isBackendUp = false
        return false
      }
      if (!force && this.hasFreshBackendState) {
        return this.isBackendUp
      }
      const result = await checkBackend({
        timeoutMs,
        onResult: () => {
          /* state is updated below; callback is for observability */
        },
      })
      this.lastHealthResult = result
      this.lastBackendCheckAt = Date.now()
      this.pendingInitialHealthCheck = false
      this.isBackendUp = result === 'ok'
      return this.isBackendUp
    },

    /**
     * Start a periodic healthcheck every `intervalMs` (default 30s). Returns
     * a teardown function that clears the interval.
     */
    startPeriodicHealthChecks({ intervalMs = DEFAULT_HEALTHCHECK_INTERVAL_MS } = {}) {
      if (typeof window === 'undefined') return () => {}
      if (this._healthInterval) return () => this.stopPeriodicHealthChecks()
      this._healthInterval = window.setInterval(() => {
        this.refreshBackendHealth().catch(() => {})
      }, intervalMs)
      return () => this.stopPeriodicHealthChecks()
    },

    stopPeriodicHealthChecks() {
      if (this._healthInterval && typeof window !== 'undefined') {
        window.clearInterval(this._healthInterval)
      }
      this._healthInterval = null
    },
  },
})
