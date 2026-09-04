import { defineStore } from 'pinia'
import api from '@/services/api'
import { queuePendingProductionRecord, SUBMISSION_KIND_FIELD, SUBMISSION_KIND_COMBUSTIBLE } from '@/services/pendingRecords'
import { useProduccionStore } from '@/stores/produccion'

const createFormUuid = () => (
  globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
)

export const useCombustibleStore = defineStore('combustible', {
  state: () => ({
    moviles: [],
    lugaresCarga: [],
    loadingMoviles: false,
    loadingLugares: false,
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

    async fetchLugaresCarga(unidadId) {
      this.lugaresCarga = []
      if (!unidadId) return []

      this.loadingLugares = true
      this.error = null
      try {
        const { data } = await api.get('/api/produccion/lugares-carga', {
          params: { un_id: unidadId },
          _suppressErrorToast: true,
        })
        this.lugaresCarga = Array.isArray(data) ? data : []
        return this.lugaresCarga
      } catch (error) {
        this.error = error.response?.data?.detail || 'No se pudieron cargar los lugares de carga'
        this.lugaresCarga = []
        return []
      } finally {
        this.loadingLugares = false
      }
    },

    async createCarga(payload) {
      this.saving = true
      this.error = null
      const submissionPayload = {
        ...payload,
        form_uuid: payload.form_uuid || createFormUuid(),
      }
      const pendingPayload = {
        ...submissionPayload,
        [SUBMISSION_KIND_FIELD]: SUBMISSION_KIND_COMBUSTIBLE,
      }

      try {
        if (!navigator.onLine) {
          await queuePendingProductionRecord(pendingPayload)
          await useProduccionStore().refreshPendingCount()
          this.lastCarga = { ...submissionPayload, offline: true }
          return this.lastCarga
        }

        const { data } = await api.post('/api/combustible/cargas', submissionPayload)
        this.lastCarga = data
        return data
      } catch (error) {
        if (!error.response || Number(error.response?.status) >= 500) {
          await queuePendingProductionRecord(pendingPayload)
          await useProduccionStore().refreshPendingCount()
          this.lastCarga = { ...submissionPayload, offline: true }
          return this.lastCarga
        }
        this.error = error.response?.data?.detail || 'No se pudo registrar la carga de combustible'
        throw error
      } finally {
        this.saving = false
      }
    },
  },
})
