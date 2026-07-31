import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

import api from '@/services/api'
import { useCombustibleStore } from './combustible'


describe('combustible store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
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
})
