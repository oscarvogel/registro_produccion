import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: { get: vi.fn() },
}))

import api from '@/services/api'
import { useDashboardStore } from './dashboard'

describe('dashboard store - metric scope', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('preserves the number of records included by the KPI response', async () => {
    api.get.mockResolvedValueOnce({
      data: {
        kpis: [{ id: 1, nombre: 'Producción', descripcion: 'Total del período', valor: 12, unidad: 'm³', icono: 'box' }],
        filtros_aplicados: {},
        registros_incluidos: 7,
      },
    })

    const store = useDashboardStore()
    store.filtros.un_id = 10

    await store.fetchKpis()

    expect(store.registrosIncluidos).toBe(7)
    expect(store.kpis[0].descripcion).toBe('Total del período')
  })
})
