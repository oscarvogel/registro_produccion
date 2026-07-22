import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const catalogRows = new Map()

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
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
      count: vi.fn(async () => 0),
      delete: vi.fn(),
      update: vi.fn(),
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
  ensurePendingIdentity: vi.fn(async (record) => ({
    ...record.payload,
    form_uuid: record.payload?.form_uuid || record.clientId,
  })),
  queuePendingProductionRecord: vi.fn(),
}))

import api from '@/services/api'
import db from '@/services/db'
import { queuePendingProductionRecord } from '@/services/pendingRecords'
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

describe('produccion sync offline', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    api.post.mockReset()
    queuePendingProductionRecord.mockReset()
    db.pendingRecords.count.mockReset().mockResolvedValue(0)
  })

  it('retries a queued record with its stable form_uuid', async () => {
    db.pendingRecords.where.mockReturnValue({
      equals: vi.fn(() => ({
        toArray: vi.fn(async () => [{
          id: 7,
          clientId: 'offline-uuid-7',
          payload: { fecha: '2026-07-21', operacion: 'PROCESO' },
          retryCount: 0,
        }]),
        count: vi.fn(async () => 0),
      })),
    })
    api.post.mockResolvedValueOnce({ data: { id: 99 } })
    const store = useProduccionStore()

    const result = await store.syncPending()

    expect(api.post).toHaveBeenCalledWith('/api/produccion/', expect.objectContaining({
      fecha: '2026-07-21',
      form_uuid: 'offline-uuid-7',
    }), expect.objectContaining({ _suppressErrorToast: true }))
    expect(db.pendingRecords.delete).toHaveBeenCalledWith(7)
    expect(result).toEqual({ successCount: 1, pendingCount: 0, permanentFailureCount: 0 })
  })

  it('reports a transient retry as still pending instead of successful', async () => {
    db.pendingRecords.count.mockResolvedValueOnce(1)
    db.pendingRecords.where.mockReturnValue({
      equals: vi.fn(() => ({
        toArray: vi.fn(async () => [{ id: 8, clientId: 'offline-uuid-8', payload: {}, retryCount: 1 }]),
        count: vi.fn(async () => 1),
      })),
    })
    api.post.mockRejectedValueOnce(new Error('network unreachable'))
    const store = useProduccionStore()

    const result = await store.syncPending()

    expect(result).toEqual({ successCount: 0, pendingCount: 1, permanentFailureCount: 0 })
  })

  it('keeps authentication failures pending so login can retry them later', async () => {
    db.pendingRecords.count.mockResolvedValueOnce(1)
    db.pendingRecords.where.mockReturnValue({
      equals: vi.fn(() => ({
        toArray: vi.fn(async () => [{ id: 10, clientId: 'offline-uuid-10', payload: {}, retryCount: 0 }]),
        count: vi.fn(async () => 1),
      })),
    })
    api.post.mockRejectedValueOnce({ response: { status: 401, data: { detail: 'Sesión expirada' } } })
    const store = useProduccionStore()

    const result = await store.syncPending()

    expect(db.pendingRecords.update).toHaveBeenLastCalledWith(10, expect.objectContaining({
      synced: 0,
      syncStatus: 'pending',
    }))
    expect(result).toEqual({ successCount: 0, pendingCount: 1, permanentFailureCount: 0 })
  })

  it('counts failed local records as requiring attention', async () => {
    db.pendingRecords.count.mockResolvedValueOnce(3)
    const store = useProduccionStore()

    await store.refreshPendingCount()

    expect(store.pendingCount).toBe(3)
  })

  it('keeps one form_uuid when an online request loses its response and is queued', async () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true })
    api.post.mockRejectedValueOnce(new Error('connection reset after commit'))
    const store = useProduccionStore()

    const result = await store.submitProduccion({ fecha: '2026-07-21' })

    const postedPayload = api.post.mock.calls[0][1]
    expect(api.post.mock.calls[0][0]).toBe('/api/produccion/')
    expect(postedPayload.form_uuid).toBeTruthy()
    expect(queuePendingProductionRecord).toHaveBeenCalledWith(postedPayload)
    expect(result).toEqual({ offline: true })
  })
})
