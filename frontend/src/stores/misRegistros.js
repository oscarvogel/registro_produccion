import { defineStore } from 'pinia'
import api from '@/services/api'

function emptyTotals() {
  return {
    total: 0,
    total_horas: 0,
    total_horas_equipo: 0,
    total_combustible: 0,
    total_tn: 0,
    total_m3: 0,
    total_has: 0,
    total_carros: 0,
    total_plantas: 0,
    total_km_carreteo: 0,
    total_km_perfilado: 0,
    total_hr_disposicion: 0,
    total_hr_remolque: 0,
    combustible_por_hora: null,
    tn_por_hora: null,
    m3_por_hora: null,
    has_por_hora: null,
    carros_por_hora: null,
    plantas_por_hora: null,
    km_carreteo_por_hora: null,
    km_perfilado_por_hora: null,
    hr_disposicion_por_hora: null,
    hr_remolque_por_hora: null,
  }
}

function round2(value) {
  return Math.round((Number(value || 0) + Number.EPSILON) * 100) / 100
}

export function calculateGroupedTotals(registros = [], resumenEquipo = null) {
  const totals = emptyTotals()
  totals.total = registros.length
  totals.total_horas = round2(registros.reduce(
    (acc, row) => acc + Math.max(Number(row.hr_fin || 0) - Number(row.hr_inicio || 0), 0),
    0,
  ))
  const combustiblePersonal = round2(
    registros.reduce((acc, row) => acc + Number(row.combustible || 0), 0),
  )
  // El libro de combustible (cargacomb) es la fuente de verdad del equipo:
  // incluye las cargas de los partes, las independientes y las manuales.
  totals.total_combustible = resumenEquipo
    ? round2(Number(resumenEquipo.total_egresos || 0))
    : combustiblePersonal
  totals.total_horas_equipo = resumenEquipo
    ? round2(Number(resumenEquipo.total_horas || 0))
    : totals.total_horas
  totals.total_tn = round2(registros.reduce((acc, row) => acc + Number(row.tn_despachadas || 0), 0))
  totals.total_m3 = round2(registros.reduce((acc, row) => acc + Number(row.m3 || 0), 0))
  totals.total_has = round2(registros.reduce((acc, row) => acc + Number(row.has || 0), 0))
  totals.total_carros = round2(registros.reduce((acc, row) => acc + Number(row.carros || 0), 0))
  totals.total_plantas = round2(registros.reduce((acc, row) => acc + Number(row.plantas || 0), 0))
  totals.total_km_carreteo = round2(registros.reduce((acc, row) => acc + Number(row.km_carreteo || 0), 0))
  totals.total_km_perfilado = round2(registros.reduce((acc, row) => acc + Number(row.km_perfilado || 0), 0))
  totals.total_hr_disposicion = round2(registros.reduce((acc, row) => acc + Number(row.hr_disposicion || 0), 0))
  totals.total_hr_remolque = round2(registros.reduce((acc, row) => acc + Number(row.hr_remolque || 0), 0))

  const perHour = (value) => totals.total_horas > 0 && Number(value) > 0
    ? round2(Number(value) / totals.total_horas)
    : null

  totals.combustible_por_hora = totals.total_horas_equipo > 0 && Number(totals.total_combustible) > 0
    ? round2(Number(totals.total_combustible) / totals.total_horas_equipo)
    : null
  totals.tn_por_hora = perHour(totals.total_tn)
  totals.m3_por_hora = perHour(totals.total_m3)
  totals.has_por_hora = perHour(totals.total_has)
  totals.carros_por_hora = perHour(totals.total_carros)
  totals.plantas_por_hora = perHour(totals.total_plantas)
  totals.km_carreteo_por_hora = perHour(totals.total_km_carreteo)
  totals.km_perfilado_por_hora = perHour(totals.total_km_perfilado)
  totals.hr_disposicion_por_hora = perHour(totals.total_hr_disposicion)
  totals.hr_remolque_por_hora = perHour(totals.total_hr_remolque)
  return totals
}

export const useMisRegistrosStore = defineStore('misRegistros', {
  state: () => ({
    registros: [],
    totales: emptyTotals(),
    resumenEquipo: null,
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

    async fetchResumenEquipo(equipoIds) {
      if (!equipoIds.length) return null
      const params = { equipos: equipoIds.join(',') }
      if (this.filtros.fecha_desde) params.fecha_desde = this.filtros.fecha_desde
      if (this.filtros.fecha_hasta) params.fecha_hasta = this.filtros.fecha_hasta
      try {
        const { data } = await api.get('/api/combustible/resumen-equipos', {
          params,
          _suppressErrorToast: true,
        })
        return data
      } catch (err) {
        console.warn('No se pudo cargar el resumen de combustible por equipo:', err)
        return null
      }
    },

    async fetchMisRegistros() {
      this.loading = true
      this.error = null
      try {
        const params = {}
        if (this.filtros.fecha_desde) params.fecha_desde = this.filtros.fecha_desde
        if (this.filtros.fecha_hasta) params.fecha_hasta = this.filtros.fecha_hasta

        const [legacyResponse, caminosResponse] = await Promise.all([
          api.get('/api/produccion/mis-registros', { params, _suppressErrorToast: true }),
          api.get('/api/produccion/caminos/mis-registros', { params, _suppressErrorToast: true }),
        ])

        const legacyRows = legacyResponse.data?.registros || []
        const caminosRows = caminosResponse.data?.registros || []
        const childIds = new Set((caminosResponse.data?.child_ids || []).map((id) => Number(id)))
        const rowsSinDuplicados = legacyRows.filter((row) => !childIds.has(Number(row.id)))

        this.registros = [...rowsSinDuplicados, ...caminosRows].sort((a, b) => {
          const fechaA = String(a.fecha || '')
          const fechaB = String(b.fecha || '')
          if (fechaA !== fechaB) return fechaB.localeCompare(fechaA)
          return Number(b.id || 0) - Number(a.id || 0)
        })
        const equipoIds = [
          ...new Set(
            this.registros
              .map((row) => Number(row.cod_equipo || 0))
              .filter((id) => id > 0),
          ),
        ]
        this.resumenEquipo = await this.fetchResumenEquipo(equipoIds)
        this.totales = calculateGroupedTotals(this.registros, this.resumenEquipo)
      } catch (err) {
        console.error('Error cargando mis registros:', err)
        this.error = 'No se pudieron cargar los registros'
        this.registros = []
        this.resumenEquipo = null
        this.totales = emptyTotals()
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