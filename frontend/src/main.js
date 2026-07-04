import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'
import App from './App.vue'
import router from './router'
import { motionPluginOptions } from '@/config/motion'
import { setUnauthorizedHandler } from '@/services/api'
import { initializeTheme } from '@/composables/useTheme'
import './style.css'

const RELOAD_AFTER_PRELOAD_ERROR_KEY = 'registro_preload_error_reloaded'

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
