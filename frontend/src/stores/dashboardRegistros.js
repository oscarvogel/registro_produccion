import { defineStore } from 'pinia'
import api from '@/services/api'

const DEFAULT_PAGE_SIZE = 20
const CAMINOS_PAGE_SIZE = 100

/** Normaliza los query params del router al estado de filtros. */
function filtrosFromQuery(query) {
  if (!query) return null
  const unId = query.un_id ? Number(query.un_id) : null
  const tipoProcesoId = query.tipo_proceso_id ? Number(query.tipo_proceso_id) : null
  const tipoProcesoKey = query.tipo_proceso_key ? String(query.tipo_proceso_key) : null
  const movilId = query.movil_id ? Number(query.movil_id) : null
  const fechaDesde = query.fecha_desde || null
  const fechaHasta = query.fecha_hasta || null
  return { unId, tipoProcesoId, tipoProcesoKey, movilId, fechaDesde, fechaHasta }
}

function buildQueryParams(filtros) {
  const params = { page: 1, page_size: DEFAULT_PAGE_SIZE }
  if (filtros.unId) params.un_id = filtros.unId
  if (filtros.tipoProcesoId) params.tipo_proceso_id = filtros.tipoProcesoId
  if (filtros.tipoProcesoKey) params.tipo_proceso_key = filtros.tipoProcesoKey
  if (filtros.movilId) params.movil_id = filtros.movilId
  if (filtros.fechaDesde) params.fecha_desde = filtros.fechaDesde
  if (filtros.fechaHasta) params.fecha_hasta = filtros.fechaHasta
  return params
}

function normalizeName(value) {
  return String(value || '').trim().toLowerCase()
}

export function groupCaminosRows(rows = []) {
  const groups = new Map()
  for (const row of rows) {
    const key = row.form_uuid ? `form:${row.form_uuid}` : `row:${row.id}`
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(row)
  }

  return Array.from(groups.values()).map((siblings) => {
    const first = siblings[0]
    if (siblings.length === 1) {
      return { ...first, procesos_count: Number(first.procesos_count || 1) }
    }

    const sum = (field) => siblings.reduce((acc, row) => acc + Number(row?.[field] || 0), 0)
    return {
      ...first,
      operacion: `Caminos — ${siblings.length} procesos`,
      procesos_count: siblings.length,
      tn_despachadas: sum('tn_despachadas'),
      m3: sum('m3'),
      has: sum('has'),
      carros: sum('carros'),
      plantas: sum('plantas'),
      km_carreteo: sum('km_carreteo'),
      km_perfilado: sum('km_perfilado'),
      hr_disposicion: sum('hr_disposicion'),
      hr_remolque: sum('hr_remolque'),
      mtrs_recorridos: sum('mtrs_recorridos'),
      // Cabecera del parte: no sumar valores replicados en filas hermanas.
      combustible: Number(first.combustible || 0),
      hrs_no_op: Number(first.hrs_no_op || 0),
    }
  })
}

export const useDashboardRegistrosStore = defineStore('dashboardRegistros', {
  state: () => ({
    registros: [],
    total: 0,
    page: 1,
    pageSize: DEFAULT_PAGE_SIZE,
    totalPages: 0,
    filtros: {
      unId: null,
      tipoProcesoId: null,
      tipoProcesoKey: null,
      movilId: null,
      fechaDesde: null,
      fechaHasta: null,
    },
    unidadEsCaminos: null,
    loading: false,
    error: null,
    detalle: null,
    detalleLoading: false,
    detalleError: null,
  }),

  getters: {
    hasRegistros: (state) => state.registros.length > 0,
    hasFiltrosAplicados: (state) => {
      return Boolean(
        state.filtros.tipoProcesoId ||
          state.filtros.tipoProcesoKey ||
          state.filtros.movilId ||
          state.filtros.fechaDesde ||
          state.filtros.fechaHasta,
      )
    },
  },

  actions: {
    /** Inicializa los filtros desde los query params del router y dispara la primera carga. */
    async initFromQuery(query) {
      const parsed = filtrosFromQuery(query)
      if (parsed) this.filtros = { ...this.filtros, ...parsed }
      this.unidadEsCaminos = null
      await this.fetchRegistros()
    },

    async resolveUnidadEsCaminos() {
      if (!this.filtros.unId) return false
      if (this.unidadEsCaminos !== null) return this.unidadEsCaminos
      try {
        const { data } = await api.get('/api/produccion/unidades-negocio', {
          _suppressErrorToast: true,
        })
        const unidad = (Array.isArray(data) ? data : []).find(
          (item) => Number(item.idUnidadNegocio) === Number(this.filtros.unId),
        )
        this.unidadEsCaminos = normalizeName(unidad?.nombre) === 'caminos'
      } catch {
        this.unidadEsCaminos = false
      }
      return this.unidadEsCaminos
    },

    async fetchRegistrosCaminos(params) {
      const firstParams = { ...params, page: 1, page_size: CAMINOS_PAGE_SIZE }
      const first = await api.get('/api/dashboard/registros', {
        params: firstParams,
        _suppressErrorToast: true,
      })
      const payload = first.data || {}
      const rows = [...(payload.items || [])]
      const pages = Number(payload.total_pages || 0)

      for (let page = 2; page <= pages; page += 1) {
        const { data } = await api.get('/api/dashboard/registros', {
          params: { ...firstParams, page },
          _suppressErrorToast: true,
        })
        rows.push(...(data.items || []))
      }

      const grouped = groupCaminosRows(rows)
      const total = grouped.length
      const totalPages = total ? Math.ceil(total / this.pageSize) : 0
      const safePage = totalPages ? Math.min(Math.max(this.page, 1), totalPages) : 1
      const start = (safePage - 1) * this.pageSize

      this.registros = grouped.slice(start, start + this.pageSize)
      this.total = total
      this.page = safePage
      this.totalPages = totalPages
    },

    async fetchRegistros() {
      if (!this.filtros.unId) {
        this.registros = []
        this.total = 0
        this.totalPages = 0
        return
      }
      this.loading = true
      this.error = null
      try {
        const params = buildQueryParams(this.filtros)
        const esCaminos = await this.resolveUnidadEsCaminos()

        if (esCaminos) {
          await this.fetchRegistrosCaminos(params)
          return
        }

        params.page = this.page
        params.page_size = this.pageSize
        const { data } = await api.get('/api/dashboard/registros', {
          params,
          _suppressErrorToast: true,
        })
        this.registros = data.items || []
        this.total = data.total || 0
        this.page = data.page || 1
        this.pageSize = data.page_size || DEFAULT_PAGE_SIZE
        this.totalPages = data.total_pages || 0
      } catch (err) {
        console.error('Error cargando registros del dashboard:', err)
        this.error = 'No se pudieron cargar los registros'
        this.registros = []
        this.total = 0
        this.totalPages = 0
      } finally {
        this.loading = false
      }
    },

    async setPage(page) {
      const parsed = Number(page) || 1
      if (parsed === this.page) return
      this.page = parsed
      await this.fetchRegistros()
    },

    async fetchDetalle(id) {
      if (!id) {
        this.detalle = null
        return
      }
      this.detalleLoading = true
      this.detalleError = null
      try {
        const { data } = await api.get(`/api/dashboard/registros/${id}`, {
          _suppressErrorToast: true,
        })
        const summary = this.registros.find((item) => Number(item.id) === Number(id))
        this.detalle = summary?.procesos_count > 1 ? { ...data, ...summary } : data
      } catch (err) {
        console.error('Error cargando detalle del registro:', err)
        this.detalleError =
          err?.response?.status === 404
            ? 'No se encontro el registro o esta fuera de tu alcance'
            : 'No se pudo cargar el detalle del registro'
        this.detalle = null
      } finally {
        this.detalleLoading = false
      }
    },

    clearDetalle() {
      this.detalle = null
      this.detalleError = null
    },

    reset() {
      this.registros = []
      this.total = 0
      this.page = 1
      this.totalPages = 0
      this.unidadEsCaminos = null
      this.filtros = {
        unId: null,
        tipoProcesoId: null,
        tipoProcesoKey: null,
        movilId: null,
        fechaDesde: null,
        fechaHasta: null,
      }
      this.loading = false
      this.error = null
    },
  },
})