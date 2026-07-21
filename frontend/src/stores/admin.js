import { defineStore } from 'pinia'
import api from '@/services/api'
import { ADMIN_ENTITY_CONFIG } from '@/config/adminEntityConfig'

export { ADMIN_ENTITY_CONFIG }

export const useAdminStore = defineStore('admin', {
  state: () => ({
    dashboard: [],
    dashboardOverview: null,
    recentRecords: [],
    usuariosConfiguracion: [],
    loading: false,
    loadingDashboardOverview: false,
    loadingRecentRecords: false,
    error: null,
    dashboardOverviewError: null,
  }),

  actions: {
    getEntityConfig(entity) {
      return ADMIN_ENTITY_CONFIG[entity] || null
    },

    async fetchEntity(entity, { skip = 0, limit = 50, buscar = '', unidad_id = null, activo = null } = {}) {
      const config = this.getEntityConfig(entity)
      if (!config) {
        throw new Error(`Entidad no soportada: ${entity}`)
      }
      const params = { skip, limit }
      if (buscar?.trim()) params.buscar = buscar.trim()
      if (unidad_id) params.unidad_id = unidad_id
      if (activo === 0 || activo === 1) params.activo = activo
      const { data } = await api.get(config.endpoint, { params })
      return data
    },

    async createEntity(entity, payload) {
      const config = this.getEntityConfig(entity)
      if (!config) {
        throw new Error(`Entidad no soportada: ${entity}`)
      }
      const { data } = await api.post(config.endpoint, payload)
      return data
    },

    async updateEntity(entity, id, payload) {
      const config = this.getEntityConfig(entity)
      if (!config) {
        throw new Error(`Entidad no soportada: ${entity}`)
      }
      const { data } = await api.put(`${config.endpoint}/${id}`, payload)
      return data
    },

    async deleteEntity(entity, id) {
      const config = this.getEntityConfig(entity)
      if (!config) {
        throw new Error(`Entidad no soportada: ${entity}`)
      }
      await api.delete(`${config.endpoint}/${id}`)
    },

    async fetchDashboard(filters = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/api/admin/dashboard', { params: filters, _suppressErrorToast: true })
        this.dashboard = data
      } catch (error) {
        this.error = error.response?.data?.detail || 'No se pudo cargar el dashboard de administracion'
        this.dashboard = []
      } finally {
        this.loading = false
      }
    },

    async fetchDashboardOverview(filters = {}) {
      this.loadingDashboardOverview = true
      this.dashboardOverviewError = null
      try {
        const { data } = await api.get('/api/admin/dashboard/overview', { params: filters, _suppressErrorToast: true })
        this.dashboardOverview = data
      } catch (error) {
        this.dashboardOverviewError = error.response?.data?.detail || 'No se pudo cargar el resumen ejecutivo'
        this.dashboardOverview = null
      } finally {
        this.loadingDashboardOverview = false
      }
    },

    async fetchRecentRecords({ fecha = null, limit = 5 } = {}) {
      this.loadingRecentRecords = true
      try {
        const params = { limit }
        if (fecha) params.fecha = fecha
        const { data } = await api.get('/api/admin/dashboard/recent-records', { params, _suppressErrorToast: true })
        this.recentRecords = data
      } catch {
        this.recentRecords = []
      } finally {
        this.loadingRecentRecords = false
      }
    },

    async fetchUsuariosConfiguracion(buscar = '') {
      this.loading = true
      this.error = null
      try {
        const params = {}
        if (buscar?.trim()) params.buscar = buscar.trim()
        const { data } = await api.get('/api/admin/configuracion/usuarios', { params, _suppressErrorToast: true })
        this.usuariosConfiguracion = data
      } catch (error) {
        this.error = error.response?.data?.detail || 'No se pudo cargar la configuracion de acceso'
        this.usuariosConfiguracion = []
      } finally {
        this.loading = false
      }
    },

    async updateAccesoUsuario(idPersonal, isAdmin) {
      const { data } = await api.patch(`/api/admin/configuracion/usuarios/${idPersonal}/acceso`, {
        is_admin: isAdmin ? 1 : 0,
      })
      return data
    },
  },
})
