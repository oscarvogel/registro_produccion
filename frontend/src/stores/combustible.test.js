import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

vi.mock('@/services/pendingRecords', () => ({
  queuePendingProductionRecord: vi.fn(),
  SUBMISSION_KIND_FIELD: '__submission_kind',
  SUBMISSION_KIND_COMBUSTIBLE: 'combustible',
}))

vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => ({ refreshPendingCount: vi.fn(async () => 1) }),
}))

import api from '@/services/api'
import { queuePendingProductionRecord } from '@/services/pendingRecords'
import { useCombustibleStore } from './combustible'


describe('combustible store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true })
  })

  it('loads places for the selected equipment business unit', async () => {
    api.get.mockResolvedValueOnce({
      data: [{ idLugarCarga: 42, detalle: 'Pañol COSECHA CTL' }],
    })
    const store = useCombustibleStore()

    await store.fetchLugaresCarga(7)

    expect(api.get).toHaveBeenCalledWith(
      '/api/produccion/lugares-carga',
      expect.objectContaining({
        params: { un_id: 7 },
        _suppressErrorToast: true,
      }),
    )
    expect(store.lugaresCarga).toEqual([
      { idLugarCarga: 42, detalle: 'Pañol COSECHA CTL' },
    ])
  })

  it('forwards the stable identity and complete inventory payload', async () => {
    const payload = {
      form_uuid: 'carga-fisica-1',
      fecha: '2026-07-29',
      id_movil: 10,
      litros: 160,
      km: 14855,
      id_lugar_carga: 42,
      id_tipo_comb: 1,
      remito: 'R-0001',
      remito2: '',
      remito3: '',
      observaciones: null,
    }
    api.post.mockResolvedValueOnce({
      data: { id_carga: 99, movil: 'FORWA-N°2', ...payload },
    })
    const store = useCombustibleStore()

    const result = await store.createCarga(payload)

    expect(api.post).toHaveBeenCalledWith('/api/combustible/cargas', payload)
    expect(result.id_carga).toBe(99)
    expect(store.lastCarga.form_uuid).toBe('carga-fisica-1')
  })

  it('queues combustible locally when offline and keeps a stable form_uuid', async () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false })
    const store = useCombustibleStore()
    const result = await store.createCarga({
      fecha: '2026-09-04',
      id_movil: 10,
      litros: 120,
      km: 15000,
      id_lugar_carga: 42,
      id_tipo_comb: 1,
      remito: 'R-9',
      remito2: '',
      remito3: '',
    })

    expect(api.post).not.toHaveBeenCalled()
    expect(queuePendingProductionRecord).toHaveBeenCalledWith(expect.objectContaining({
      __submission_kind: 'combustible',
      form_uuid: expect.any(String),
    }))
    expect(result.offline).toBe(true)
    expect(result.form_uuid).toBeTruthy()
  })

  it('queues combustible locally when backend/MySQL responds 503', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 503, data: { detail: 'DB unavailable' } } })
    const store = useCombustibleStore()
    const result = await store.createCarga({
      form_uuid: 'comb-503',
      fecha: '2026-09-04',
      id_movil: 10,
      litros: 120,
      km: 15000,
      id_lugar_carga: 42,
      id_tipo_comb: 1,
      remito: 'R-10',
      remito2: '',
      remito3: '',
    })

    expect(queuePendingProductionRecord).toHaveBeenCalledWith(expect.objectContaining({
      __submission_kind: 'combustible',
      form_uuid: 'comb-503',
    }))
    expect(result).toEqual(expect.objectContaining({ offline: true, form_uuid: 'comb-503' }))
  })
})
