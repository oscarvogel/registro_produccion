import { defineStore } from 'pinia'
import api from '@/services/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    kpis: [],
    evolucion: { labels: [], datasets: [] },
    rankingMaquinas: [],
    filtros: {
      un_id: null,
      tipo_proceso_id: null,
      movil_id: null,
      fecha_desde: null,
      fecha_hasta: null,
    },
    filtrosAplicados: {},
    tiposProceso: [],
    movilesDisponibles: [],
    loading: {
      kpis: false,
      evolucion: false,
      ranking: false,
    },
    error: null,
  }),

  getters: {
    kpiPrincipal: (state) => state.kpis.find((k) => k.es_principal) || null,
    kpisSecundarios: (state) => state.kpis.filter((k) => !k.es_principal),
    isLoading: (state) => state.loading.kpis || state.loading.evolucion || state.loading.ranking,
    filtrosActivos: (state) => {
      let count = 0
      if (state.filtros.tipo_proceso_id) count++
      if (state.filtros.movil_id) count++
      if (state.filtros.fecha_desde) count++
      if (state.filtros.fecha_hasta) count++
      return count
    },
  },

  actions: {
    _buildParams() {
      const params = { un_id: this.filtros.un_id }
      if (this.filtros.tipo_proceso_id) params.tipo_proceso_id = this.filtros.tipo_proceso_id
      if (this.filtros.movil_id) params.movil_id = this.filtros.movil_id
      if (this.filtros.fecha_desde) params.fecha_desde = this.filtros.fecha_desde
      if (this.filtros.fecha_hasta) params.fecha_hasta = this.filtros.fecha_hasta
      return params
    },

    async loadTiposProceso(unId) {
      try {
        const { data } = await api.get('/api/dashboard/tipos-proceso-disponibles', {
          params: { un_id: unId },
        })
        this.tiposProceso = data
      } catch (err) {
        console.error('Error cargando tipos de proceso:', err)
        this.tiposProceso = []
      }
    },

    async loadMovilesDisponibles(unId, tipoProcesoId = null) {
      try {
        const params = { un_id: unId }
        if (tipoProcesoId) params.tipo_proceso_id = tipoProcesoId
        const { data } = await api.get('/api/dashboard/moviles-disponibles', { params })
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
        const { data } = await api.get('/api/dashboard/kpis', { params: this._buildParams() })
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
        const { data } = await api.get('/api/dashboard/evolucion', { params: this._buildParams() })
        this.evolucion = data
      } catch (err) {
        console.error('Error cargando evolución:', err)
        this.evolucion = { labels: [], datasets: [] }
      } finally {
        this.loading.evolucion = false
      }
    },

    async fetchRanking() {
      if (!this.filtros.un_id) return
      this.loading.ranking = true
      try {
        const { data } = await api.get('/api/dashboard/ranking-maquinas', { params: this._buildParams() })
        this.rankingMaquinas = data
      } catch (err) {
        console.error('Error cargando ranking:', err)
        this.rankingMaquinas = []
      } finally {
        this.loading.ranking = false
      }
    },

    async fetchAll() {
      await Promise.all([this.fetchKpis(), this.fetchEvolucion(), this.fetchRanking()])
    },

    async setFiltro(campo, valor) {
      this.filtros[campo] = valor

      // Si cambia tipo_proceso, resetear movil y recargar móviles disponibles
      if (campo === 'tipo_proceso_id') {
        this.filtros.movil_id = null
        await this.loadMovilesDisponibles(this.filtros.un_id, valor)
      }

      await this.fetchAll()
    },

    limpiarFiltros() {
      this.filtros.tipo_proceso_id = null
      this.filtros.movil_id = null
      // Reset fechas al mes actual
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      this.filtros.fecha_desde = `${y}-${m}-01`
      const lastDay = new Date(y, now.getMonth() + 1, 0).getDate()
      this.filtros.fecha_hasta = `${y}-${m}-${String(lastDay).padStart(2, '0')}`
      this.fetchAll()
    },

    initFiltros(unId) {
      this.filtros.un_id = unId
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      this.filtros.fecha_desde = `${y}-${m}-01`
      const lastDay = new Date(y, now.getMonth() + 1, 0).getDate()
      this.filtros.fecha_hasta = `${y}-${m}-${String(lastDay).padStart(2, '0')}`
    },
  },
})
