import { defineStore } from 'pinia'
import api from '@/services/api'
import db from '@/services/db'
import { queuePendingProductionRecord } from '@/services/pendingRecords'
import {
  contarEvidenciasPendientes,
  listarEvidenciasPendientes,
  marcarEvidenciaConError,
  marcarEvidenciaSincronizada,
  queuePendingEvidencia,
} from '@/services/pendingEvidencias'
import { useToastStore } from '@/stores/toast'
import {
  extractApiErrorMessage,
  extractValidationErrorMessage,
  normalizeProduccionPayload,
} from '@/utils/apiError'

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

const createFormUuid = () => (
  globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`
)

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
    selectedUnId: null,
    movilAsignado: null,
    actas: [],
    predios: [],
    rodales: [],
    lugaresCarga: [],
    pendingCount: 0,
    // Fotos de evidencia encoladas todavia sin subir (decision D3).
    pendingEvidenceCount: 0,
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
        const config = params ? { params } : {}
        config._suppressErrorToast = true
        const { data } = await api.get(url, config)
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
      this.selectedUnId = unId || null
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
        const params = this.selectedUnId ? { un_id: this.selectedUnId } : undefined
        const { data } = await api.get(`/api/produccion/movil-by-operador/${operadorId}`, { params })
        this.movilAsignado = data
      } catch (err) {
        console.error('Error loading movil:', err)
      }
    },

    async fetchAsignaciones(operadorId) {
      if (!operadorId) {
        this.asignaciones = []
        return []
      }

      const allowedProcessIds = new Set(
        ensureArray(this.tiposProceso)
          .map((tipo) => Number(tipo.id))
          .filter((id) => Number.isInteger(id) && id > 0),
      )
      const scope = `${operadorId}:un:${this.selectedUnId || 'all'}`
      const items = await this.fetchCatalog({
        catalog: 'asignaciones',
        target: 'asignaciones',
        url: `/api/produccion/asignaciones/${operadorId}`,
        params: this.selectedUnId ? { un_id: this.selectedUnId } : undefined,
        scope,
        skipWhenMissingScope: false,
      })

      // Defensa adicional del frontend: una asignacion nunca puede inyectar
      // un proceso que no figure en el catalogo habilitado de la UN actual.
      // Esto tambien protege contra cache vieja/offline.
      if (['success', 'empty'].includes(this.catalogStatus.tiposProceso?.state)) {
        const filtered = ensureArray(items).filter((asig) => {
          const processId = Number(asig.idProceso)
          return Number.isInteger(processId) && allowedProcessIds.has(processId)
        })
        this.asignaciones = filtered
        if (filtered.length !== items.length) {
          await this.saveCatalogCache('asignaciones', scope, filtered)
        }
        return filtered
      }

      return items
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

    // Issue #133: lista de rodales vinculados al Acta seleccionada.
    // El dropdown del parte usa esta lista cuando hay un Acta elegida;
    // si ademas hay un Predio elegido, se filtra client-side.
    async fetchRodalesPorActa(actaNumero) {
      const numero = (actaNumero || '').toString().trim()
      if (!numero) return null
      return this.fetchCatalog({
        catalog: 'rodales',
        target: 'rodales',
        url: `/api/produccion/actas/${encodeURIComponent(numero)}/rodales`,
        scope: `acta:${numero}`,
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

    // Sube una foto de evidencia (issue #200). La foto viaja suelta, con el
    // `form_uuid` del formulario; el backend la vincula al registro cuando
    // se crea.
    async uploadEvidencia({ formUuid, tipo, archivo, incluyeHorometro = false }) {
      const formData = new FormData()
      formData.append('form_uuid', formUuid)
      formData.append('tipo', tipo)
      formData.append('incluye_horometro', incluyeHorometro ? 'true' : 'false')
      formData.append('archivo', archivo, archivo?.name || 'evidencia.jpg')
      const { data } = await api.post('/api/produccion/evidencias', formData, {
        // multipart: si se deja el Content-Type por defecto (json), axios
        // manda el FormData como JSON y el backend no lo entiende.
        headers: { 'Content-Type': 'multipart/form-data' },
        _suppressErrorToast: true,
      })
      return data
    },

    // Encola las fotos de evidencia del formulario (decision D3). La foto
    // queda en el telefono hasta que vuelva la senal.
    async encolarEvidencias({ formUuid, fotos = [] }) {
      const encoladas = []
      for (const foto of fotos) {
        if (!foto?.blob) continue
        const id = await queuePendingEvidencia({
          formUuid,
          tipo: foto.tipo,
          blob: foto.blob,
          incluyeHorometro: Boolean(foto.incluyeHorometro),
          nombre: foto.nombre,
        })
        encoladas.push(id)
      }
      await this.refreshPendingEvidenceCount()
      return encoladas
    },

    // Sube las fotos encoladas de un formulario y devuelve los ids de la
    // evidencia (los que van en el payload del parte). El upload es
    // idempotente por (form_uuid, tipo): si la foto ya estaba en el
    // servidor, devuelve la misma fila y no duplica.
    async subirEvidenciasPendientes(formUuid) {
      const pendientes = await listarEvidenciasPendientes(formUuid)
      const ids = []
      for (const fila of pendientes) {
        try {
          const respuesta = await this.uploadEvidencia({
            formUuid: fila.formUuid,
            tipo: fila.tipo,
            archivo: fila.blob,
            incluyeHorometro: Boolean(fila.incluyeHorometro),
          })
          ids.push(respuesta.id)
          await marcarEvidenciaSincronizada(fila.id)
        } catch (err) {
          await marcarEvidenciaConError(
            fila.id,
            extractApiErrorMessage(err, 'No se pudo subir la foto de evidencia.'),
          )
          throw err
        }
      }
      await this.refreshPendingEvidenceCount()
      return ids
    },

    async refreshPendingEvidenceCount() {
      this.pendingEvidenceCount = await contarEvidenciasPendientes()
    },

    async submitProduccion(formData) {
      this.submitting = true
      this.error = null
      const submissionPayload = normalizeProduccionPayload({
        ...formData,
        form_uuid: formData.form_uuid || createFormUuid(),
      })
      try {
        // If offline, queue locally instead of posting
        if (!navigator.onLine) {
          await queuePendingProductionRecord(submissionPayload)
          await this.refreshPendingCount()
          useToastStore().info(
            'Guardado solo en este teléfono',
            'Todavía no está confirmado por el servidor. Podés verificarlo en Pendientes.',
          )
          return { offline: true }
        }

        const { data } = await api.post('/api/produccion/', submissionPayload)
        useToastStore().success('Registro guardado')
        return data
      } catch (err) {
        // Network error → queue for later
        if (!err.response || Number(err.response?.status) >= 500) {
          await queuePendingProductionRecord(submissionPayload)
          await this.refreshPendingCount()
          useToastStore().info(
            'Guardado solo en este teléfono',
            'El servidor no confirmó la recepción. El registro permanece en Pendientes.',
          )
          return { offline: true }
        }
        const isValidation = err.response?.status === 422
        const message = isValidation
          ? extractValidationErrorMessage(err, 'No se pudo guardar el registro. Revisa los datos del formulario.')
          : extractApiErrorMessage(err, 'No se pudo guardar el registro')
        this.error = message
        useToastStore().error('No se pudo guardar', message)
        throw err
      } finally {
        this.submitting = false
      }
    },

    async refreshPendingCount() {
      this.pendingCount = await db.pendingRecords.count()
    },

    // NOTA: `syncPending` NO vive en este store. `stores/produccion.js` (el
    // store que usa la app) lo reemplaza por una version que ademas sabe
    // que tipo de parte es el que se sincroniza (`produccion`, `caminos`,
    // `combustible`). Tener dos copias de la regla de sync hacia que la
    // evidencia se suba antes que el parte (decision D3) era una fuente de
    // divergencia: la copia de aca nunca se ejecutaba.

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