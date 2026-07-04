import { defineStore } from 'pinia'

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
 *   - `isBackendUp`  → placeholder for the healthcheck from issue #49.
 *                       Today it follows `isOnline`; once #49 lands the real
 *                       check will replace it without touching the UI.
 *
 * Call `useConnectivityStore().init()` once from `main.js` so the listeners
 * are registered at boot.
 */
export const useConnectivityStore = defineStore('connectivity', {
  state: () => ({
    isOnline: readInitialOnline(),
    isBackendUp: readInitialOnline(),
    lastBackendCheckAt: 0,
  }),

  getters: {
    isOffline: (state) => state.isOnline === false,
    isOfflineOrBackendDown: (state) =>
      state.isOnline === false || state.isBackendUp === false,
  },

  actions: {
    _setOnline(value) {
      this.isOnline = value
      if (!value) {
        // If we just lost the link to the network, the backend is also down
        // from our perspective until proven otherwise.
        this.isBackendUp = false
      } else {
        // Coming back online does NOT mean the backend is healthy — that
        // requires a real healthcheck (issue #49). Until then, optimistically
        // assume it is.
        this.isBackendUp = true
        this.lastBackendCheckAt = Date.now()
      }
    },

    init() {
      if (typeof window === 'undefined') return
      if (this._initialized) return
      this._initialized = true

      // Sync once before listening.
      this._setOnline(readInitialOnline())

      window.addEventListener('online', () => this._setOnline(true))
      window.addEventListener('offline', () => this._setOnline(false))
    },
  },
})
