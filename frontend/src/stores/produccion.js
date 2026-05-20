import { defineStore } from 'pinia'
import api from '@/services/api'
import db from '@/services/db'
import { queuePendingProductionRecord } from '@/services/pendingRecords'
import { useToastStore } from '@/stores/toast'

const ensureArray = (value) => (Array.isArray(value) ? value : [])
const CATALOG_TTL_MS = 5 * 60 * 1000

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
    lugaresCarga: [],
    pendingCount: 0,
    catalogosLoadedAt: 0,
    loading: false,
    submitting: false,
    syncingPending: false,
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

    async fetchLugaresCarga(unId) {
      this.lugaresCarga = []
      if (!unId) return
      try {
        const { data } = await api.get('/api/produccion/lugares-carga', {
          params: { un_id: unId },
        })
        this.lugaresCarga = ensureArray(data)
      } catch (err) {
        console.error('Error loading lugares de carga:', err)
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
        // If offline, queue locally instead of posting
        if (!navigator.onLine) {
          await queuePendingProductionRecord(formData)
          await this.refreshPendingCount()
          useToastStore().info('Registro guardado offline', 'Se sincronizara cuando vuelva la conexion.')
          return { offline: true }
        }

        const { data } = await api.post('/api/produccion', formData)
        useToastStore().success('Registro guardado')
        return data
      } catch (err) {
        // Network error → queue for later
        if (!err.response) {
          await queuePendingProductionRecord(formData)
          await this.refreshPendingCount()
          useToastStore().info('Registro guardado offline', 'No hubo conexion con el servidor; quedo en cola.')
          return { offline: true }
        }
        this.error = err.response?.data?.detail || 'Error al guardar el registro'
        useToastStore().error('No se pudo guardar', this.error)
        throw err
      } finally {
        this.submitting = false
      }
    },

    async refreshPendingCount() {
      this.pendingCount = await db.pendingRecords.where('synced').equals(0).count()
    },

    async syncPending() {
      if (this.syncingPending) return 0
      this.syncingPending = true
      const pending = await db.pendingRecords.where('synced').equals(0).toArray()
      if (!pending.length) {
        this.syncingPending = false
        return 0
      }

      this.error = null
      let successCount = 0
      let permanentFailureCount = 0

      try {
        for (const record of pending) {
          try {
            await db.pendingRecords.update(record.id, {
              syncStatus: 'syncing',
              lastAttemptAt: Date.now(),
              retryCount: Number(record.retryCount || 0) + 1,
            })
            await api.post('/api/produccion', record.payload)
            await db.pendingRecords.delete(record.id)
            successCount++
          } catch (err) {
            const status = err?.response?.status

            if (status >= 400 && status < 500) {
              const detail = err.response?.data?.detail || 'Error permanente al sincronizar el registro'
              await db.pendingRecords.update(record.id, {
                synced: 1,
                syncStatus: 'failed',
                syncError: detail,
                failedAt: Date.now(),
              })
              permanentFailureCount++
              continue
            }

            await db.pendingRecords.update(record.id, {
              syncStatus: 'pending',
              syncError: err.response?.data?.detail || 'Error transitorio. Se reintentara automaticamente.',
            })
          }
        }

        await this.refreshPendingCount()
        if (permanentFailureCount > 0) {
          this.error = `No se pudieron sincronizar ${permanentFailureCount} registro(s) por un error permanente.`
          useToastStore().error('Sincronizacion parcial', this.error)
        } else if (successCount > 0) {
          useToastStore().success('Pendientes sincronizados', `${successCount} registro(s) enviados.`)
        }
        return successCount
      } finally {
        this.syncingPending = false
      }
    },

    // Carga inicial de catálogos
    async loadCatalogos({ force = false } = {}) {
      const isFresh = this.catalogosLoadedAt && Date.now() - this.catalogosLoadedAt < CATALOG_TTL_MS
      if (!force && isFresh && this.unidadesNegocio.length > 0 && this.todosLosTipos.length > 0) {
        await this.refreshPendingCount()
        return
      }

      this.loading = true
      try {
        await Promise.all([
          this.fetchUnidadesNegocio(),
          this.fetchActas(),
          this.fetchPredios(),
          this.fetchAllTiposProceso(),
        ])
        this.catalogosLoadedAt = Date.now()
        await this.refreshPendingCount()
      } finally {
        this.loading = false
      }
    },
  },
})
