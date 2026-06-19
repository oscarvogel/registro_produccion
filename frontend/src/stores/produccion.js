import { defineStore } from 'pinia'
import api from '@/services/api'
import db from '@/services/db'
import { queuePendingProductionRecord } from '@/services/pendingRecords'
import { useToastStore } from '@/stores/toast'

const ensureArray = (value) => (Array.isArray(value) ? value : [])
const CATALOG_TTL_MS = 5 * 60 * 1000
const CATALOG_KEYS = [
  'unidadesNegocio',
  'operadores',
  'moviles',
  'tiposProceso',
  'todosLosTipos',
  'actas',
  'predios',
  'rodales',
  'lugaresCarga',
  'asignaciones',
]

const createCatalogState = () => ({
  state: 'idle',
  stale: false,
  lastError: null,
  updatedAt: 0,
})

const createCatalogStatus = () => Object.fromEntries(
  CATALOG_KEYS.map((key) => [key, createCatalogState()]),
)

const catalogCacheKey = (catalog, scope = '') => `${catalog}:${scope || 'all'}`

const errorMessage = (err) => err?.response?.data?.detail || err?.message || 'No se pudo cargar el catalogo'

function isValidCatalogPayload(data) {
  return Array.isArray(data)
}

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
    catalogStatus: createCatalogStatus(),
  }),

  actions: {
    setCatalogStatus(catalog, patch) {
      this.catalogStatus[catalog] = {
        ...this.catalogStatus[catalog],
        ...patch,
      }
    },

    async saveCatalogCache(catalog, scope, items) {
      if (!db.catalogos || !isValidCatalogPayload(items)) return
      await db.catalogos.put({
        key: catalogCacheKey(catalog, scope),
        catalog,
        scope: String(scope || 'all'),
        items,
        timestamp: Date.now(),
      })
    },

    async loadCatalogFallback(catalog, scope) {
      if (!db.catalogos) return null
      const cached = await db.catalogos.get(catalogCacheKey(catalog, scope))
      if (!cached || !isValidCatalogPayload(cached.items)) return null
      return cached
    },

    async fetchCatalog({ catalog, target, url, params, scope = 'all', skipWhenMissingScope = false }) {
      if (skipWhenMissingScope && !scope) {
        this[target] = []
        this.setCatalogStatus(catalog, createCatalogState())
        return []
      }

      this.setCatalogStatus(catalog, {
        state: 'loading',
        stale: this.catalogStatus[catalog]?.stale || false,
        lastError: null,
      })

      try {
        const { data } = await api.get(url, params ? { params } : undefined)
        if (!isValidCatalogPayload(data)) {
          throw new Error('Respuesta invalida del servidor')
        }
        const items = ensureArray(data)
        this[target] = items
        await this.saveCatalogCache(catalog, scope, items)
        this.setCatalogStatus(catalog, {
          state: items.length > 0 ? 'success' : 'empty',
          stale: false,
          lastError: null,
          updatedAt: Date.now(),
        })
        return items
      } catch (err) {
        const cached = await this.loadCatalogFallback(catalog, scope)
        if (cached) {
          this[target] = cached.items
          this.setCatalogStatus(catalog, {
            state: cached.items.length > 0 ? 'success' : 'empty',
            stale: true,
            lastError: errorMessage(err),
            updatedAt: cached.timestamp || 0,
          })
          return cached.items
        }

        this.setCatalogStatus(catalog, {
          state: 'error',
          stale: false,
          lastError: errorMessage(err),
        })
        console.error(`Error loading ${catalog}:`, err)
        return this[target]
      }
    },

    async fetchOperadores(unId) {
      return this.fetchCatalog({
        catalog: 'operadores',
        target: 'operadores',
        url: '/api/produccion/operadores',
        params: { un_id: unId },
        scope: unId,
        skipWhenMissingScope: true,
      })
    },

    async fetchMoviles(unId) {
      return this.fetchCatalog({
        catalog: 'moviles',
        target: 'moviles',
        url: '/api/produccion/moviles',
        params: { un_id: unId },
        scope: unId,
        skipWhenMissingScope: true,
      })
    },

    async fetchUnidadesNegocio() {
      return this.fetchCatalog({
        catalog: 'unidadesNegocio',
        target: 'unidadesNegocio',
        url: '/api/produccion/unidades-negocio',
      })
    },

    async fetchTiposProceso(unId) {
      return this.fetchCatalog({
        catalog: 'tiposProceso',
        target: 'tiposProceso',
        url: '/api/produccion/tipo-proceso',
        params: { un_id: unId },
        scope: unId,
        skipWhenMissingScope: true,
      })
    },

    async fetchAllTiposProceso() {
      return this.fetchCatalog({
        catalog: 'todosLosTipos',
        target: 'todosLosTipos',
        url: '/api/produccion/tipos-proceso-all',
      })
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
      return this.fetchCatalog({
        catalog: 'asignaciones',
        target: 'asignaciones',
        url: `/api/produccion/asignaciones/${operadorId}`,
        scope: operadorId,
        skipWhenMissingScope: true,
      })
    },

    async fetchActas() {
      return this.fetchCatalog({
        catalog: 'actas',
        target: 'actas',
        url: '/api/produccion/actas',
      })
    },

    async fetchPredios() {
      return this.fetchCatalog({
        catalog: 'predios',
        target: 'predios',
        url: '/api/produccion/predios',
      })
    },

    async fetchRodales(predioId) {
      return this.fetchCatalog({
        catalog: 'rodales',
        target: 'rodales',
        url: '/api/produccion/rodales',
        params: { predio_id: predioId },
        scope: predioId,
        skipWhenMissingScope: true,
      })
    },

    async fetchLugaresCarga(unId) {
      return this.fetchCatalog({
        catalog: 'lugaresCarga',
        target: 'lugaresCarga',
        url: '/api/produccion/lugares-carga',
        params: { un_id: unId },
        scope: unId,
        skipWhenMissingScope: true,
      })
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
        const criticalCatalogs = ['unidadesNegocio', 'actas', 'predios', 'todosLosTipos']
        const allCriticalLoaded = criticalCatalogs.every((catalog) => this.catalogStatus[catalog]?.state !== 'error')
        if (allCriticalLoaded) {
          this.catalogosLoadedAt = Date.now()
        }
        await this.refreshPendingCount()
      } finally {
        this.loading = false
      }
    },

    async retryCatalogo(catalog, scope) {
      const retryMap = {
        unidadesNegocio: () => this.fetchUnidadesNegocio(),
        operadores: () => this.fetchOperadores(scope),
        moviles: () => this.fetchMoviles(scope),
        tiposProceso: () => this.fetchTiposProceso(scope),
        todosLosTipos: () => this.fetchAllTiposProceso(),
        actas: () => this.fetchActas(),
        predios: () => this.fetchPredios(),
        rodales: () => this.fetchRodales(scope),
        lugaresCarga: () => this.fetchLugaresCarga(scope),
        asignaciones: () => this.fetchAsignaciones(scope),
      }
      return retryMap[catalog]?.()
    },
  },
})
