import { defineStore } from 'pinia'
import api from '@/services/api'

const ensureArray = (value) => (Array.isArray(value) ? value : [])

export const useProduccionStore = defineStore('produccion', {
  state: () => ({
    operadores: [],
    moviles: [],
    asignaciones: [],
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
        this.operadores = ensureArray(data)
      } catch (err) {
        console.error('Error loading operadores:', err)
      }
    },

    async fetchMoviles(unId) {
      this.moviles = []
      if (!unId) return
      try {
        const { data } = await api.get('/api/produccion/moviles', {
          params: { un_id: unId },
        })
        this.moviles = ensureArray(data)
      } catch (err) {
        console.error('Error loading moviles:', err)
      }
    },

    async fetchUnidadesNegocio() {
      try {
        const { data } = await api.get('/api/produccion/unidades-negocio')
        this.unidadesNegocio = ensureArray(data)
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
        this.tiposProceso = ensureArray(data)
      } catch (err) {
        console.error('Error loading tipos de proceso:', err)
      }
    },

    async fetchAllTiposProceso() {
      try {
        const { data } = await api.get('/api/produccion/tipos-proceso-all')
        this.todosLosTipos = ensureArray(data)
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

    async fetchAsignaciones(operadorId) {
      this.asignaciones = []
      if (!operadorId) return
      try {
        const { data } = await api.get(`/api/produccion/asignaciones/${operadorId}`)
        this.asignaciones = ensureArray(data)
      } catch (err) {
        console.error('Error loading asignaciones:', err)
      }
    },

    async fetchActas() {
      try {
        const { data } = await api.get('/api/produccion/actas')
        this.actas = ensureArray(data)
      } catch (err) {
        console.error('Error loading actas:', err)
      }
    },

    async fetchPredios() {
      try {
        const { data } = await api.get('/api/produccion/predios')
        this.predios = ensureArray(data)
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
        this.rodales = ensureArray(data)
      } catch (err) {
        console.error('Error loading rodales:', err)
      }
    },

    async fetchUltimaHoraFin(params) {
      try {
        const { data } = await api.get('/api/produccion/ultima-hora-fin', { params })
        return data
      } catch (err) {
        console.error('Error loading ultima hora fin:', err)
        return null
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
