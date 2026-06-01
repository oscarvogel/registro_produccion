import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'
import App from './App.vue'
import router from './router'
import { motionPluginOptions } from '@/config/motion'
import { setUnauthorizedHandler } from '@/services/api'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(MotionPlugin, motionPluginOptions)

// Restore auth header on app init
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.initAuth()

setUnauthorizedHandler(() => {
  authStore.logout()
  if (router.currentRoute.value.name !== 'login') {
    router.push({ name: 'login' })
  }
})

app.mount('#app')
