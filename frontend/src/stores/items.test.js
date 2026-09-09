import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import { useItemsStore } from './items'

describe('items store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('separa el error de carga del estado vacio y permite reintentar', async () => {
    api.get.mockRejectedValueOnce({ response: { data: { detail: 'Servicio temporalmente no disponible' } } })
    const store = useItemsStore()

    await store.fetchItems()

    expect(store.error).toBe('Servicio temporalmente no disponible')
    expect(store.items).toEqual([])
    expect(api.get).toHaveBeenCalledWith('/api/items', { _suppressErrorToast: true })

    api.get.mockResolvedValueOnce({ data: [{ id: 1, name: 'Item 1' }] })
    await store.fetchItems()

    expect(store.error).toBeNull()
    expect(store.items).toHaveLength(1)
  })
})
