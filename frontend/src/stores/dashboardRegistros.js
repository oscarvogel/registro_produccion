import { defineStore } from 'pinia'
import api from '@/services/api'

const DEFAULT_PAGE_SIZE = 20

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
      await this.fetchRegistros()
    },

    async fetchRegistros() {
      if (!this.filtros.unId) {
        // Sin unidad no hay listado: se limpia y se sale sin pegar al backend.
        this.registros = []
        this.total = 0
        this.totalPages = 0
        return
      }
      this.loading = true
      this.error = null
      try {
        const params = buildQueryParams(this.filtros)
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
        this.detalle = data
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
