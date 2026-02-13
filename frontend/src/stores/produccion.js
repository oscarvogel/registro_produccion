import { defineStore } from 'pinia'
import api from '@/services/api'

export const useProduccionStore = defineStore('produccion', {
  state: () => ({
    operadores: [],
    unidadesNegocio: [],
    tiposProceso: [],
    todosLosTipos: [],
    movilAsignado: null,
    actas: [],
    predios: [],
    rodales: [],
    loading: false,
    submitting: false,
    error: null,
  }),

  actions: {
    async fetchOperadores(unId) {
      this.operadores = []
      if (!unId) return
      try {
        const { data } = await api.get('/api/produccion/operadores', {
          params: { un_id: unId },
        })
        this.operadores = data
      } catch (err) {
        console.error('Error loading operadores:', err)
      }
    },

    async fetchUnidadesNegocio() {
      try {
        const { data } = await api.get('/api/produccion/unidades-negocio')
        this.unidadesNegocio = data
      } catch (err) {
        console.error('Error loading unidades de negocio:', err)
      }
    },

    async fetchTiposProceso(unId) {
      this.tiposProceso = []
      if (!unId) return
      try {
        const { data } = await api.get('/api/produccion/tipo-proceso', {
          params: { un_id: unId },
        })
        this.tiposProceso = data
      } catch (err) {
        console.error('Error loading tipos de proceso:', err)
      }
    },

    async fetchAllTiposProceso() {
      try {
        const { data } = await api.get('/api/produccion/tipos-proceso-all')
        this.todosLosTipos = data
      } catch (err) {
        console.error('Error loading all tipos de proceso:', err)
      }
    },

    async fetchMovilByOperador(operadorId) {
      this.movilAsignado = null
      if (!operadorId) return
      try {
        const { data } = await api.get(`/api/produccion/movil-by-operador/${operadorId}`)
        this.movilAsignado = data
      } catch (err) {
        console.error('Error loading movil:', err)
      }
    },

    async fetchActas() {
      try {
        const { data } = await api.get('/api/produccion/actas')
        this.actas = data
      } catch (err) {
        console.error('Error loading actas:', err)
      }
    },

    async fetchPredios() {
      try {
        const { data } = await api.get('/api/produccion/predios')
        this.predios = data
      } catch (err) {
        console.error('Error loading predios:', err)
      }
    },

    async fetchRodales(predioId) {
      this.rodales = []
      if (!predioId) return
      try {
        const { data } = await api.get('/api/produccion/rodales', {
          params: { predio_id: predioId },
        })
        this.rodales = data
      } catch (err) {
        console.error('Error loading rodales:', err)
      }
    },

    async submitProduccion(formData) {
      this.submitting = true
      this.error = null
      try {
        const { data } = await api.post('/api/produccion', formData)
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Error al guardar el registro'
        throw err
      } finally {
        this.submitting = false
      }
    },

    // Carga inicial de catálogos
    async loadCatalogos() {
      this.loading = true
      try {
        await Promise.all([
          this.fetchUnidadesNegocio(),
          this.fetchActas(),
          this.fetchPredios(),
          this.fetchAllTiposProceso(),
        ])
      } finally {
        this.loading = false
      }
    },
  },
})
