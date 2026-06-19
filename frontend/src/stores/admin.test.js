import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    put: vi.fn(),
  },
}))

import api from '@/services/api'
import { useAdminStore } from './admin'

describe('admin store tipos de proceso requirements', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('sends location requirement flags when creating a process type', async () => {
    api.post.mockResolvedValueOnce({ data: { id: 12 } })
    const store = useAdminStore()
    const payload = {
      nombre: 'Cosecha selectiva',
      unidad_ids: [1],
      requiere_acta: true,
      requiere_predio: false,
      requiere_rodal: true,
      activo: 1,
    }

    await store.createEntity('tipos-proceso', payload)

    expect(api.post).toHaveBeenCalledWith('/api/admin/tipos-proceso', payload)
  })

  it('sends location requirement flags when updating a process type', async () => {
    api.put.mockResolvedValueOnce({ data: { id: 12 } })
    const store = useAdminStore()
    const payload = {
      nombre: 'Cosecha selectiva',
      unidad_ids: [1],
      requiere_acta: false,
      requiere_predio: true,
      requiere_rodal: false,
      activo: 1,
    }

    await store.updateEntity('tipos-proceso', 12, payload)

    expect(api.put).toHaveBeenCalledWith('/api/admin/tipos-proceso/12', payload)
  })
})
