import { defineStore } from 'pinia'
import api from '@/services/api'

export const useMisRegistrosStore = defineStore('misRegistros', {
  state: () => ({
    registros: [],
    totales: {
      total: 0,
      total_horas: 0,
      total_combustible: 0,
      total_tn: 0,
      total_m3: 0,
      total_has: 0,
      total_carros: 0,
      total_plantas: 0,
      total_km_carreteo: 0,
      total_km_perfilado: 0,
      combustible_por_hora: null,
      tn_por_hora: null,
      m3_por_hora: null,
      has_por_hora: null,
      carros_por_hora: null,
      plantas_por_hora: null,
      km_carreteo_por_hora: null,
      km_perfilado_por_hora: null,
    },
    filtros: {
      fecha_desde: null,
      fecha_hasta: null,
    },
    loading: false,
    error: null,
  }),

  actions: {
    initFiltros() {
      const now = new Date()
      const y = now.getFullYear()
      const m = String(now.getMonth() + 1).padStart(2, '0')
      this.filtros.fecha_desde = `${y}-${m}-01`
      const lastDay = new Date(y, now.getMonth() + 1, 0).getDate()
      this.filtros.fecha_hasta = `${y}-${m}-${String(lastDay).padStart(2, '0')}`
    },

    async fetchMisRegistros() {
      this.loading = true
      this.error = null
      try {
        const params = {}
        if (this.filtros.fecha_desde) params.fecha_desde = this.filtros.fecha_desde
        if (this.filtros.fecha_hasta) params.fecha_hasta = this.filtros.fecha_hasta

        const { data } = await api.get('/api/produccion/mis-registros', { params })
        this.registros = data.registros
        this.totales = {
          total: data.total,
          total_horas: data.total_horas,
          total_combustible: data.total_combustible,
          total_tn: data.total_tn,
          total_m3: data.total_m3,
          total_has: data.total_has,
          total_carros: data.total_carros,
          total_plantas: data.total_plantas,
          total_km_carreteo: data.total_km_carreteo,
          total_km_perfilado: data.total_km_perfilado,
          combustible_por_hora: data.combustible_por_hora,
          tn_por_hora: data.tn_por_hora,
          m3_por_hora: data.m3_por_hora,
          has_por_hora: data.has_por_hora,
          carros_por_hora: data.carros_por_hora,
          plantas_por_hora: data.plantas_por_hora,
          km_carreteo_por_hora: data.km_carreteo_por_hora,
          km_perfilado_por_hora: data.km_perfilado_por_hora,
        }
      } catch (err) {
        console.error('Error cargando mis registros:', err)
        this.error = 'No se pudieron cargar los registros'
        this.registros = []
      } finally {
        this.loading = false
      }
    },

    async setFiltro(campo, valor) {
      this.filtros[campo] = valor
      await this.fetchMisRegistros()
    },

    limpiarFiltros() {
      this.initFiltros()
      this.fetchMisRegistros()
    },
  },
})
