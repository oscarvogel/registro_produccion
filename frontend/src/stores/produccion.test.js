import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const mockState = vi.hoisted(() => {
  let nextId = 1
  const catalogRows = new Map()
  const records = []

  const makePendingQuery = (field, value) => ({
    count: vi.fn(async () => records.filter((record) => record[field] === value).length),
    toArray: vi.fn(async () => records.filter((record) => record[field] === value).map((record) => ({ ...record }))),
  })

  const addPendingRecord = (payload, overrides = {}) => {
    const record = {
      id: nextId++,
      payload,
      timestamp: Date.now(),
      synced: 0,
      syncStatus: 'pending',
      retryCount: 0,
      ...overrides,
    }
    records.push(record)
    return record
  }

  return {
    catalogRows,
    records,
    reset() {
      nextId = 1
      catalogRows.clear()
      records.splice(0, records.length)
    },
    addPendingRecord,
    apiGet: vi.fn(),
    apiPost: vi.fn(),
    queuePendingProductionRecord: vi.fn(async (payload) => addPendingRecord(payload).id),
    pendingRecords: {
      where: vi.fn((field) => ({
        equals: vi.fn((value) => makePendingQuery(field, value)),
      })),
      update: vi.fn(async (id, changes) => {
        const record = records.find((item) => item.id === id)
        if (!record) return 0
        Object.assign(record, changes)
        return 1
      }),
      delete: vi.fn(async (id) => {
        const index = records.findIndex((item) => item.id === id)
        if (index >= 0) records.splice(index, 1)
      }),
    },
    toast: {
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn(),
    },
  }
})

vi.mock('@/services/api', () => ({
  default: {
    get: mockState.apiGet,
    post: mockState.apiPost,
  },
  getUserSafeErrorMessage: (error, fallback) => error?.response?.data?.detail || fallback,
}))

vi.mock('@/services/db', () => ({
  default: {
    catalogos: {
      put: vi.fn(async (row) => {
        mockState.catalogRows.set(row.key, row)
      }),
      get: vi.fn(async (key) => mockState.catalogRows.get(key)),
    },
    pendingRecords: mockState.pendingRecords,
  },
}))

vi.mock('@/services/pendingRecords', () => ({
  queuePendingProductionRecord: mockState.queuePendingProductionRecord,
}))

vi.mock('@/stores/toast', () => ({
  useToastStore: () => mockState.toast,
}))

import api from '@/services/api'
import db from '@/services/db'
import { useProduccionStore } from './produccion'

function setOnline(value) {
  Object.defineProperty(window.navigator, 'onLine', {
    configurable: true,
    value,
  })
}

describe('produccion catalogos offline', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setOnline(true)
    mockState.reset()
    vi.clearAllMocks()
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
    mockState.catalogRows.set('operadores:7', {
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
})

describe('produccion offline queue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setOnline(true)
    mockState.reset()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('queues a production record when the browser is offline', async () => {
    const store = useProduccionStore()
    const payload = { fecha: '2026-06-16', cod_operador: 7, produccion: 12 }

    setOnline(false)
    const result = await store.submitProduccion(payload)

    expect(result).toEqual({ offline: true })
    expect(api.post).not.toHaveBeenCalled()
    expect(mockState.queuePendingProductionRecord).toHaveBeenCalledWith(payload)
    expect(store.pendingCount).toBe(1)
    expect(mockState.records[0]).toMatchObject({
      payload,
      synced: 0,
      syncStatus: 'pending',
    })
  })

  it('queues a production record when the backend is unreachable', async () => {
    const store = useProduccionStore()
    const payload = { fecha: '2026-06-16', cod_operador: 8, produccion: 9 }
    api.post.mockRejectedValueOnce(new Error('Network Error'))

    const result = await store.submitProduccion(payload)

    expect(result).toEqual({ offline: true })
    expect(mockState.queuePendingProductionRecord).toHaveBeenCalledWith(payload)
    expect(store.pendingCount).toBe(1)
  })

  it('syncs queued records and removes them after a successful post', async () => {
    const store = useProduccionStore()
    const payload = { fecha: '2026-06-16', cod_operador: 9, produccion: 18 }
    mockState.addPendingRecord(payload)
    api.post.mockResolvedValueOnce({ data: { id: 123 } })

    const count = await store.syncPending()

    expect(count).toBe(1)
    expect(api.post).toHaveBeenCalledWith('/api/produccion', payload)
    expect(mockState.records).toHaveLength(0)
    expect(store.pendingCount).toBe(0)
    expect(store.syncingPending).toBe(false)
  })

  it('keeps 4xx sync errors as failed records for manual review', async () => {
    const store = useProduccionStore()
    const payload = { fecha: '2026-06-16', cod_operador: 10, produccion: 0 }
    mockState.addPendingRecord(payload)
    api.post.mockRejectedValueOnce({
      response: { status: 422, data: { detail: 'Produccion invalida' } },
    })

    const count = await store.syncPending()

    expect(count).toBe(0)
    expect(mockState.records).toHaveLength(1)
    expect(mockState.records[0]).toMatchObject({
      payload,
      synced: 1,
      syncStatus: 'failed',
      syncError: 'Produccion invalida',
    })
    expect(store.pendingCount).toBe(0)
    expect(store.error).toContain('error permanente')
  })

  it('keeps transient sync errors pending and exposes a retryable error', async () => {
    const store = useProduccionStore()
    const payload = { fecha: '2026-06-16', cod_operador: 11, produccion: 5 }
    mockState.addPendingRecord(payload)
    api.post.mockRejectedValueOnce(new Error('Network Error'))

    const count = await store.syncPending()

    expect(count).toBe(0)
    expect(mockState.records).toHaveLength(1)
    expect(mockState.records[0]).toMatchObject({
      payload,
      synced: 0,
      syncStatus: 'pending',
      syncError: 'Error transitorio. Se reintentara automaticamente.',
    })
    expect(store.pendingCount).toBe(1)
    expect(store.error).toContain('error transitorio')
    expect(store.syncingPending).toBe(false)
  })
})
