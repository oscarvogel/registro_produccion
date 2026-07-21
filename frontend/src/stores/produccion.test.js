import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const catalogRows = new Map()

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

vi.mock('@/services/db', () => ({
  default: {
    catalogos: {
      put: vi.fn(async (row) => {
        catalogRows.set(row.key, row)
      }),
      get: vi.fn(async (key) => catalogRows.get(key)),
    },
    pendingRecords: {
      where: vi.fn(() => ({
        equals: vi.fn(() => ({
          count: vi.fn(async () => 0),
          toArray: vi.fn(async () => []),
        })),
      })),
    },
  },
}))

vi.mock('@/services/pendingRecords', () => ({
  queuePendingProductionRecord: vi.fn(),
}))

import api from '@/services/api'
import db from '@/services/db'
import { useProduccionStore } from './produccion'

describe('produccion catalogos offline', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    catalogRows.clear()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('caches a successful catalog response and marks it as loaded', async () => {
    api.get.mockResolvedValueOnce({ data: [{ idPersonal: 1, nombre: 'Ada' }] })
    const store = useProduccionStore()

    await store.fetchOperadores(7)

    expect(store.operadores).toEqual([{ idPersonal: 1, nombre: 'Ada' }])
    expect(db.catalogos.put).toHaveBeenCalledWith(expect.objectContaining({
      key: 'operadores:7',
      catalog: 'operadores',
      items: [{ idPersonal: 1, nombre: 'Ada' }],
    }))
    expect(store.catalogStatus.operadores.state).toBe('success')
    expect(store.catalogStatus.operadores.stale).toBe(false)
  })

  it('preserves previous data and uses cached fallback when a catalog request fails', async () => {
    catalogRows.set('operadores:7', {
      key: 'operadores:7',
      catalog: 'operadores',
      items: [{ idPersonal: 2, nombre: 'Grace' }],
      timestamp: 1000,
    })
    api.get.mockRejectedValueOnce(new Error('network down'))
    const store = useProduccionStore()
    store.operadores = [{ idPersonal: 1, nombre: 'Ada' }]

    await store.fetchOperadores(7)

    expect(store.operadores).toEqual([{ idPersonal: 2, nombre: 'Grace' }])
    expect(store.catalogStatus.operadores.state).toBe('success')
    expect(store.catalogStatus.operadores.stale).toBe(true)
    expect(store.catalogStatus.operadores.lastError).toContain('network down')
  })

  it('keeps previous data and marks error when fetch fails without fallback', async () => {
    api.get.mockRejectedValueOnce(new Error('server exploded'))
    const store = useProduccionStore()
    store.moviles = [{ idMovil: 10, detalle: 'Forwarder' }]

    await store.fetchMoviles(3)

    expect(store.moviles).toEqual([{ idMovil: 10, detalle: 'Forwarder' }])
    expect(store.catalogStatus.moviles.state).toBe('error')
    expect(store.catalogStatus.moviles.lastError).toContain('server exploded')
  })

  it('treats a successful empty response as a real empty catalog', async () => {
    api.get.mockResolvedValueOnce({ data: [] })
    const store = useProduccionStore()
    store.tiposProceso = [{ id: 1, nombre: 'PROCESO' }]

    await store.fetchTiposProceso(5)

    expect(store.tiposProceso).toEqual([])
    expect(store.catalogStatus.tiposProceso.state).toBe('empty')
    expect(store.catalogStatus.tiposProceso.stale).toBe(false)
  })

  it('passes _suppressErrorToast so the global toast stays silent when the catalog shows its own fallback', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useProduccionStore()

    await store.fetchOperadores(7)

    expect(api.get).toHaveBeenCalledWith(
      '/api/produccion/operadores',
      expect.objectContaining({ _suppressErrorToast: true, params: { un_id: 7 } }),
    )
  })

  it('passes _suppressErrorToast on catalog fetches without params', async () => {
    api.get.mockResolvedValueOnce({ data: [{ id: 1 }] })
    const store = useProduccionStore()

    await store.fetchUnidadesNegocio()

    expect(api.get).toHaveBeenCalledWith(
      '/api/produccion/unidades-negocio',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
  })
})
