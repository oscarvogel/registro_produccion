import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Restore auth header on app init
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.initAuth()

app.mount('#app')
