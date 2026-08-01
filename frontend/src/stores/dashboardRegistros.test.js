import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import { useDashboardRegistrosStore } from './dashboardRegistros'

describe('dashboardRegistros store (issue #104)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('initFromQuery parsea un_id, tipo_proceso_key, movil_id y fechas del query', async () => {
    api.get.mockResolvedValueOnce({
      data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
    })
    const store = useDashboardRegistrosStore()

    await store.initFromQuery({
      un_id: '7',
      tipo_proceso_key: 'tipo:3',
      movil_id: '11',
      fecha_desde: '2026-07-01',
      fecha_hasta: '2026-07-31',
    })

    expect(store.filtros.unId).toBe(7)
    expect(store.filtros.tipoProcesoKey).toBe('tipo:3')
    expect(store.filtros.movilId).toBe(11)
    expect(store.filtros.fechaDesde).toBe('2026-07-01')
    expect(store.filtros.fechaHasta).toBe('2026-07-31')
    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/registros',
      expect.objectContaining({
        _suppressErrorToast: true,
        params: expect.objectContaining({
          un_id: 7,
          tipo_proceso_key: 'tipo:3',
          movil_id: 11,
          fecha_desde: '2026-07-01',
          fecha_hasta: '2026-07-31',
          page: 1,
          page_size: 20,
        }),
      }),
    )
  })

  it('fetchRegistros sin unId no pega al backend y limpia el estado', async () => {
    const store = useDashboardRegistrosStore()

    await store.fetchRegistros()

    expect(api.get).not.toHaveBeenCalled()
    expect(store.registros).toEqual([])
    expect(store.total).toBe(0)
    expect(store.totalPages).toBe(0)
  })

  it('fetchRegistros guarda items, total y totalPages del response', async () => {
    api.get.mockResolvedValueOnce({
      data: {
        items: [{ id: 1, fecha: '2026-07-15' }],
        total: 42,
        page: 1,
        page_size: 20,
        total_pages: 3,
      },
    })
    const store = useDashboardRegistrosStore()
    store.filtros.unId = 7

    await store.fetchRegistros()

    expect(store.registros).toHaveLength(1)
    expect(store.total).toBe(42)
    expect(store.totalPages).toBe(3)
    expect(store.error).toBeNull()
  })

  it('fetchRegistros cae a estado vacio si el backend falla y suprime el toast', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useDashboardRegistrosStore()
    store.filtros.unId = 7

    await store.fetchRegistros()

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/registros',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.registros).toEqual([])
    expect(store.error).toBe('No se pudieron cargar los registros')
  })

  it('setPage cambia la pagina y vuelve a fetchear', async () => {
    api.get.mockResolvedValue({
      data: { items: [], total: 100, page: 1, page_size: 20, total_pages: 5 },
    })
    const store = useDashboardRegistrosStore()
    store.filtros.unId = 7
    await store.fetchRegistros()

    api.get.mockClear()
    api.get.mockResolvedValueOnce({
      data: { items: [], total: 100, page: 3, page_size: 20, total_pages: 5 },
    })

    await store.setPage(3)

    expect(store.page).toBe(3)
    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/registros',
      expect.objectContaining({
        params: expect.objectContaining({ page: 3, page_size: 20 }),
      }),
    )
  })

  it('setPage con la misma pagina no vuelve a fetchear', async () => {
    api.get.mockResolvedValueOnce({
      data: { items: [], total: 0, page: 1, page_size: 20, total_pages: 0 },
    })
    const store = useDashboardRegistrosStore()
    store.filtros.unId = 7
    await store.fetchRegistros()
    api.get.mockClear()

    await store.setPage(1)
    expect(api.get).not.toHaveBeenCalled()
  })

  it('fetchDetalle carga el detalle del registro y limpia el error', async () => {
    api.get.mockResolvedValueOnce({
      data: { id: 99, fecha: '2026-07-15', operacion: 'Cosecha' },
    })
    const store = useDashboardRegistrosStore()

    await store.fetchDetalle(99)

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/registros/99',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.detalle).toEqual({ id: 99, fecha: '2026-07-15', operacion: 'Cosecha' })
    expect(store.detalleError).toBeNull()
  })

  it('fetchDetalle reporta mensaje de 404 cuando el registro no existe o esta fuera de alcance', async () => {
    const err = new Error('Not found')
    err.response = { status: 404, data: { detail: 'Registro no encontrado' } }
    api.get.mockRejectedValueOnce(err)
    const store = useDashboardRegistrosStore()

    await store.fetchDetalle(999)

    expect(store.detalle).toBeNull()
    expect(store.detalleError).toMatch(/fuera de tu alcance/i)
  })

  it('fetchDetalle reporta mensaje generico para 5xx u otros errores', async () => {
    const err = new Error('boom')
    err.response = { status: 500 }
    api.get.mockRejectedValueOnce(err)
    const store = useDashboardRegistrosStore()

    await store.fetchDetalle(1)

    expect(store.detalle).toBeNull()
    expect(store.detalleError).toBe('No se pudo cargar el detalle del registro')
  })

  it('clearDetalle resetea el detalle y el error', async () => {
    api.get.mockResolvedValueOnce({ data: { id: 1 } })
    const store = useDashboardRegistrosStore()
    await store.fetchDetalle(1)

    store.clearDetalle()
    expect(store.detalle).toBeNull()
    expect(store.detalleError).toBeNull()
  })

  it('hasFiltrosAplicados detecta filtros opcionales activos', () => {
    const store = useDashboardRegistrosStore()
    expect(store.hasFiltrosAplicados).toBe(false)

    store.filtros.movilId = 5
    expect(store.hasFiltrosAplicados).toBe(true)

    store.filtros.movilId = null
    store.filtros.fechaDesde = '2026-07-01'
    expect(store.hasFiltrosAplicados).toBe(true)

    store.filtros.fechaDesde = null
    store.filtros.tipoProcesoKey = 'tipo:3'
    expect(store.hasFiltrosAplicados).toBe(true)
  })

  it('reset limpia todos los filtros y contadores', () => {
    const store = useDashboardRegistrosStore()
    store.filtros.unId = 7
    store.filtros.movilId = 3
    store.total = 42

    store.reset()

    expect(store.filtros.unId).toBeNull()
    expect(store.filtros.movilId).toBeNull()
    expect(store.total).toBe(0)
    expect(store.registros).toEqual([])
  })
})
