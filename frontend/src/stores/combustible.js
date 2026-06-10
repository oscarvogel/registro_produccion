import { defineStore } from 'pinia'
import api from '@/services/api'

export const useCombustibleStore = defineStore('combustible', {
  state: () => ({
    moviles: [],
    loadingMoviles: false,
    saving: false,
    error: null,
    lastCarga: null,
  }),

  actions: {
    async fetchMoviles(buscar = '') {
      this.loadingMoviles = true
      this.error = null
      try {
        const params = {}
        if (buscar?.trim()) params.buscar = buscar.trim()
        const { data } = await api.get('/api/combustible/moviles', { params })
        this.moviles = data
      } catch (error) {
        this.error = error.response?.data?.detail || 'No se pudieron cargar los moviles disponibles'
        this.moviles = []
      } finally {
        this.loadingMoviles = false
      }
    },

    async createCarga(payload) {
      this.saving = true
      this.error = null
      try {
        const { data } = await api.post('/api/combustible/cargas', payload)
        this.lastCarga = data
        return data
      } catch (error) {
        this.error = error.response?.data?.detail || 'No se pudo registrar la carga de combustible'
        throw error
      } finally {
        this.saving = false
      }
    },
  },
})
