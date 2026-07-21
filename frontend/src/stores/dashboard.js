import { defineStore } from 'pinia'
import api from '@/services/api'

const DASHBOARD_FILTERS_KEY = 'dashboard_filters'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    kpis: [],
    evolucion: { labels: [], datasets: [] },
    evolucionCombustible: { labels: [], datasets: [] },
    rankingMaquinas: [],
    filtros: {
      un_id: null,
      tipo_proceso_key: null,
      evolucion_tipo_proceso_key: null,
      ranking_tipo_proceso_key: null,
      ranking_metric: 'produccion',
      movil_id: null,
      fecha_desde: null,
      fecha_hasta: null,
    },
    filtrosAplicados: {},
    unidadesNegocio: [],
    tiposProceso: [],
    movilesDisponibles: [],
    loading: {
      kpis: false,
      evolucion: false,
      evolucionCombustible: false,
      ranking: false,
    },
    error: null,
  }),

  getters: {
    kpiPrincipal: (state) => state.kpis.find((k) => k.es_principal) || null,
    kpisSecundarios: (state) => state.kpis.filter((k) => !k.es_principal),
    isLoading: (state) => state.loading.kpis || state.loading.evolucion || state.loading.evolucionCombustible || state.loading.ranking,
    filtrosActivos: (state) => {
      let count = 0
      if (state.filtros.tipo_proceso_key) count++
      if (state.filtros.movil_id) count++
      if (state.filtros.fecha_desde) count++
      if (state.filtros.fecha_hasta) count++
      return count
    },
  },

  actions: {
    _buildParams({ tipoProcesoKey = this.filtros.tipo_proceso_key, metric = null } = {}) {
      const params = { un_id: this.filtros.un_id }
      if (tipoProcesoKey) params.tipo_proceso_key = tipoProcesoKey
      if (metric) params.metric = metric
      if (this.filtros.movil_id) params.movil_id = this.filtros.movil_id
      if (this.filtros.fecha_desde) params.fecha_desde = this.filtros.fecha_desde
      if (this.filtros.fecha_hasta) params.fecha_hasta = this.filtros.fecha_hasta
      return params
    },

    async loadUnidadesNegocio() {
      try {
        const { data } = await api.get('/api/produccion/unidades-negocio', { _suppressErrorToast: true })
        this.unidadesNegocio = Array.isArray(data) ? data : []
      } catch (err) {
        console.error('Error cargando unidades de negocio:', err)
        this.unidadesNegocio = []
      }
    },

    async loadTiposProceso(unId) {
      try {
        const { data } = await api.get('/api/dashboard/tipos-proceso-disponibles', {
          params: { un_id: unId },
          _suppressErrorToast: true,
        })
        this.tiposProceso = data
      } catch (err) {
        console.error('Error cargando tipos de proceso:', err)
        this.tiposProceso = []
      }
    },

    async loadMovilesDisponibles(unId, tipoProcesoKey = null) {
      try {
        const params = { un_id: unId }
        if (tipoProcesoKey) params.tipo_proceso_key = tipoProcesoKey
        const { data } = await api.get('/api/dashboard/moviles-disponibles', { params, _suppressErrorToast: true })
        this.movilesDisponibles = data
      } catch (err) {
        console.error('Error cargando móviles:', err)
        this.movilesDisponibles = []
      }
    },

    async fetchKpis() {
      if (!this.filtros.un_id) return
      this.loading.kpis = true
      this.error = null
      try {
        const { data } = await api.get('/api/dashboard/kpis', { params: this._buildParams(), _suppressErrorToast: true })
        this.kpis = data.kpis
        this.filtrosAplicados = data.filtros_aplicados
      } catch (err) {
        console.error('Error cargando KPIs:', err)
        this.error = 'Error al cargar los KPIs'
        this.kpis = []
      } finally {
        this.loading.kpis = false
      }
    },

    async fetchEvolucion() {
      if (!this.filtros.un_id) return
      this.loading.evolucion = true
      try {
        const { data } = await api.get('/api/dashboard/evolucion', {
          params: this._buildParams({
            tipoProcesoKey: this.filtros.evolucion_tipo_proceso_key || this.filtros.tipo_proceso_key,
            metric: 'produccion',
          }),
          _suppressErrorToast: true,
        })
        this.evolucion = data
      } catch (err) {
        console.error('Error cargando evolución:', err)
        this.evolucion = { labels: [], datasets: [] }
      } finally {
        this.loading.evolucion = false
      }
    },

    async fetchEvolucionCombustible() {
      if (!this.filtros.un_id) return
      this.loading.evolucionCombustible = true
      try {
        const { data } = await api.get('/api/dashboard/evolucion', {
          params: this._buildParams({
            tipoProcesoKey: this.filtros.evolucion_tipo_proceso_key || this.filtros.tipo_proceso_key,
            metric: 'combustible',
          }),
          _suppressErrorToast: true,
        })
        this.evolucionCombustible = data
      } catch (err) {
        console.error('Error cargando evolucion de combustible:', err)
        this.evolucionCombustible = { labels: [], datasets: [] }
      } finally {
        this.loading.evolucionCombustible = false
      }
    },

    async fetchRanking() {
      if (!this.filtros.un_id) return
      this.loading.ranking = true
      try {
        const { data } = await api.get('/api/dashboard/ranking-maquinas', {
          params: this._buildParams({
            tipoProcesoKey: this.filtros.ranking_tipo_proceso_key || this.filtros.tipo_proceso_key,
            metric: this.filtros.ranking_metric,
          }),
          _suppressErrorToast: true,
        })
        this.rankingMaquinas = data
      } catch (err) {
        console.error('Error cargando ranking:', err)
        this.rankingMaquinas = []
      } finally {
        this.loading.ranking = false
      }
    },

    async fetchAll() {
      await Promise.all([this.fetchKpis(), this.fetchEvolucion(), this.fetchEvolucionCombustible(), this.fetchRanking()])
    },

    async setFiltro(campo, valor) {
      this.filtros[campo] = valor

      // Si cambia tipo_proceso, resetear movil y recargar móviles disponibles
      if (campo === 'tipo_proceso_key') {
        this.filtros.movil_id = null
        await this.loadMovilesDisponibles(this.filtros.un_id, valor)
      }

      await this.fetchAll()
      this.persistFiltros()
    },

    async setEvolucionTipoProceso(value) {
      this.filtros.evolucion_tipo_proceso_key = value || null
      await Promise.all([this.fetchEvolucion(), this.fetchEvolucionCombustible()])
      this.persistFiltros()
    },

    async setRankingTipoProceso(value) {
      this.filtros.ranking_tipo_proceso_key = value || null
      await this.fetchRanking()
      this.persistFiltros()
    },

    async setRankingMetric(value) {
      this.filtros.ranking_metric = value || 'produccion'
      await this.fetchRanking()
      this.persistFiltros()
    },

    async setUnidadNegocio(unId) {
      const parsed = unId ? Number(unId) : null
      if (!parsed || parsed === Number(this.filtros.un_id || 0)) return

      this.filtros.un_id = parsed
      this.filtros.tipo_proceso_key = null
      this.filtros.evolucion_tipo_proceso_key = null
      this.filtros.ranking_tipo_proceso_key = null
      this.filtros.movil_id = null
      this.tiposProceso = []
      this.movilesDisponibles = []

      await Promise.all([
        this.loadTiposProceso(parsed),
        this.loadMovilesDisponibles(parsed),
      ])
      await this.fetchAll()
      this.persistFiltros()
    },

    limpiarFiltros() {
      this.filtros.tipo_proceso_key = null
      this.filtros.evolucion_tipo_proceso_key = null
      this.filtros.ranking_tipo_proceso_key = null
      this.filtros.movil_id = null
      // Reset fechas al mes actual
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      this.filtros.fecha_desde = `${y}-${m}-01`
      const lastDay = new Date(y, now.getMonth() + 1, 0).getDate()
      this.filtros.fecha_hasta = `${y}-${m}-${String(lastDay).padStart(2, '0')}`
      this.fetchAll()
      this.persistFiltros()
    },

    initFiltros(unId) {
      const saved = this.loadPersistedFiltros()
      this.filtros.un_id = unId || saved.un_id || null
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      this.filtros.fecha_desde = saved.fecha_desde || `${y}-${m}-01`
      const lastDay = new Date(y, now.getMonth() + 1, 0).getDate()
      this.filtros.fecha_hasta = saved.fecha_hasta || `${y}-${m}-${String(lastDay).padStart(2, '0')}`
      this.filtros.tipo_proceso_key = saved.tipo_proceso_key || (saved.tipo_proceso_id ? `tipo:${saved.tipo_proceso_id}` : null)
      this.filtros.evolucion_tipo_proceso_key = saved.evolucion_tipo_proceso_key || null
      this.filtros.ranking_tipo_proceso_key = saved.ranking_tipo_proceso_key || null
      this.filtros.ranking_metric = saved.ranking_metric || 'produccion'
      this.filtros.movil_id = saved.movil_id || null
    },

    persistFiltros() {
      localStorage.setItem(DASHBOARD_FILTERS_KEY, JSON.stringify({
        un_id: this.filtros.un_id,
        tipo_proceso_key: this.filtros.tipo_proceso_key,
        evolucion_tipo_proceso_key: this.filtros.evolucion_tipo_proceso_key,
        ranking_tipo_proceso_key: this.filtros.ranking_tipo_proceso_key,
        ranking_metric: this.filtros.ranking_metric,
        movil_id: this.filtros.movil_id,
        fecha_desde: this.filtros.fecha_desde,
        fecha_hasta: this.filtros.fecha_hasta,
      }))
    },

    loadPersistedFiltros() {
      try {
        return JSON.parse(localStorage.getItem(DASHBOARD_FILTERS_KEY) || '{}')
      } catch {
        localStorage.removeItem(DASHBOARD_FILTERS_KEY)
        return {}
      }
    },
  },
})
