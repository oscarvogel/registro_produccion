import { defineStore } from 'pinia'
import api from '@/services/api'

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

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    loading: false,
    syncing: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !isTokenExpired(state.token),
    userName: (state) => state.user?.nombre || '',
  },

  actions: {
    async login(dni, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/api/auth/login', { dni, password })
        this.token = data.access_token
        this.user = data.user
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        // Set default auth header for future requests
        api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
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

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
    },

    // Restore auth header on app init
    initAuth() {
      if (this.token && !isTokenExpired(this.token)) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      } else {
        this.logout()
      }
    },
  },
})
