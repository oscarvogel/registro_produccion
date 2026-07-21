import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import { useDashboardStore } from './dashboard'

describe('dashboard store - toast suppression on local fallback', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('loadUnidadesNegocio passes _suppressErrorToast to skip the global toast when fallback is shown', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()

    await store.loadUnidadesNegocio()

    expect(api.get).toHaveBeenCalledWith(
      '/api/produccion/unidades-negocio',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.unidadesNegocio).toEqual([])
  })

  it('loadTiposProceso passes _suppressErrorToast when falling back to empty list', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()

    await store.loadTiposProceso(7)

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/tipos-proceso-disponibles',
      expect.objectContaining({ _suppressErrorToast: true, params: { un_id: 7 } }),
    )
    expect(store.tiposProceso).toEqual([])
  })

  it('loadMovilesDisponibles passes _suppressErrorToast when falling back to empty list', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()

    await store.loadMovilesDisponibles(7)

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/moviles-disponibles',
      expect.objectContaining({ _suppressErrorToast: true, params: { un_id: 7 } }),
    )
    expect(store.movilesDisponibles).toEqual([])
  })

  it('fetchKpis passes _suppressErrorToast when falling back to empty kpis', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()
    store.filtros.un_id = 1

    await store.fetchKpis()

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/kpis',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.kpis).toEqual([])
  })

  it('fetchEvolucion passes _suppressErrorToast when falling back to empty chart', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()
    store.filtros.un_id = 1

    await store.fetchEvolucion()

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/evolucion',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.evolucion).toEqual({ labels: [], datasets: [] })
  })

  it('fetchEvolucionCombustible passes _suppressErrorToast when falling back to empty chart', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()
    store.filtros.un_id = 1

    await store.fetchEvolucionCombustible()

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/evolucion',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.evolucionCombustible).toEqual({ labels: [], datasets: [] })
  })

  it('fetchRanking passes _suppressErrorToast when falling back to empty ranking', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardStore()
    store.filtros.un_id = 1
    store.filtros.ranking_metric = 'produccion'

    await store.fetchRanking()

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/ranking-maquinas',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.rankingMaquinas).toEqual([])
  })
})