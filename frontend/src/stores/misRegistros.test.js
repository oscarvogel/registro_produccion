import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import { useMisRegistrosStore } from './misRegistros'

describe('misRegistros store - toast suppression on local fallback', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('fetchMisRegistros passes _suppressErrorToast when falling back to empty registros', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useMisRegistrosStore()
    store.initFiltros()

    await store.fetchMisRegistros()

    expect(api.get).toHaveBeenCalledWith(
      '/api/produccion/mis-registros',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.registros).toEqual([])
    expect(store.error).toBe('No se pudieron cargar los registros')
  })
})