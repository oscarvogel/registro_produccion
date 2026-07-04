import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'
import { registerSW } from 'virtual:pwa-register'
import App from './App.vue'
import router from './router'
import { motionPluginOptions } from '@/config/motion'
import { setUnauthorizedHandler } from '@/services/api'
import { initializeTheme } from '@/composables/useTheme'
import './style.css'

const RELOAD_AFTER_PRELOAD_ERROR_KEY = 'registro_preload_error_reloaded'
const SW_RELOAD_KEY = 'registro_sw_reloaded_at'

window.addEventListener('vite:preloadError', async (event) => {
  event.preventDefault()
  if (sessionStorage.getItem(RELOAD_AFTER_PRELOAD_ERROR_KEY) === '1') return
  sessionStorage.setItem(RELOAD_AFTER_PRELOAD_ERROR_KEY, '1')

  if ('caches' in window) {
    const cacheNames = await caches.keys()
    await Promise.all(cacheNames.map((cacheName) => caches.delete(cacheName)))
  }

  if ('serviceWorker' in navigator) {
    const registrations = await navigator.serviceWorker.getRegistrations()
    await Promise.all(registrations.map((registration) => registration.update()))
  }

  window.location.reload()
})

window.addEventListener('load', () => {
  sessionStorage.removeItem(RELOAD_AFTER_PRELOAD_ERROR_KEY)
})

// Service worker — auto-update + self reload on a new build.
//
// PWA was stuck on the old bundle every time we shipped because the worker
// the operator had installed activated `skipWaiting: true` but the page
// itself never reloaded to pick the new assets. This hook forces a reload
// the moment a new service worker takes control, so the operator on the
// phone gets the latest toast fix / healthcheck / UI without having to
// hard-reload manually.
const updateSW = registerSW({
  immediate: true,
  onNeedRefresh() {
    // Avoid reload loops if something else is misbehaving.
    const lastReload = Number(sessionStorage.getItem(SW_RELOAD_KEY) || '0')
    const recent = Date.now() - lastReload < 30_000
    if (recent) return
    sessionStorage.setItem(SW_RELOAD_KEY, String(Date.now()))
    updateSW(true).then(() => {
      window.location.reload()
    }).catch(() => {
      /* SW update rejected — keep going on the old version. */
    })
  },
  onOfflineReady() {
    /* no-op for now; we already announce offline mode via the banner. */
  },
  onRegisterError(error) {
    // Logged for observability; the app still works without a SW.
    // eslint-disable-next-line no-console
    console.warn('Service worker registration failed:', error)
  },
})

const app = createApp(App)
const pinia = createPinia()

initializeTheme()

app.use(pinia)
app.use(router)
app.use(MotionPlugin, motionPluginOptions)

// Restore auth header on app init
import { useAuthStore } from '@/stores/auth'
import { useConnectivityStore } from '@/stores/connectivity'

const authStore = useAuthStore()
const connectivityStore = useConnectivityStore()
connectivityStore.init()

const initMode = authStore.initAuth()

// Kick a first healthcheck so the OfflineBanner can switch to its red
// backend-down variant within a few seconds if the backend is down. We do
// NOT block app mount on this — the layout renders with the optimistic
// `isOnline` initial value.
connectivityStore.refreshBackendHealth().catch(() => {
  /* the store already stores the latest state */
})
// Then keep checking periodically.
connectivityStore.startPeriodicHealthChecks()

if (initMode === 'offline') {
  // Notify the operator after mount that we booted in offline mode.
  // Defer one tick so the toast host is mounted.
  setTimeout(() => {
    import('./stores/toast').then(({ useToastStore }) => {
      useToastStore().info(
        'Modo offline',
        'Estás sin conexión. Tu sesión guardada te deja entrar por un tiempo limitado.',
      )
    })
  }, 0)
}

setUnauthorizedHandler(() => {
  authStore.logout()
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login' })
  }
})

app.mount('#app')
