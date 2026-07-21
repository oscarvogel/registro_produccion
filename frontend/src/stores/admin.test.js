import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
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

describe('admin store - toast suppression on local fallback', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('fetchDashboard passes _suppressErrorToast when falling back to empty list', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useAdminStore()

    await store.fetchDashboard({ un_id: 1 })

    expect(api.get).toHaveBeenCalledWith(
      '/api/admin/dashboard',
      expect.objectContaining({ _suppressErrorToast: true, params: { un_id: 1 } }),
    )
    expect(store.dashboard).toEqual([])
  })

  it('fetchDashboardOverview passes _suppressErrorToast when falling back to null', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useAdminStore()

    await store.fetchDashboardOverview({ un_id: 1 })

    expect(api.get).toHaveBeenCalledWith(
      '/api/admin/dashboard/overview',
      expect.objectContaining({ _suppressErrorToast: true, params: { un_id: 1 } }),
    )
    expect(store.dashboardOverview).toBeNull()
  })

  it('fetchRecentRecords passes _suppressErrorToast when falling back to empty list', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useAdminStore()

    await store.fetchRecentRecords({ limit: 5 })

    expect(api.get).toHaveBeenCalledWith(
      '/api/admin/dashboard/recent-records',
      expect.objectContaining({ _suppressErrorToast: true, params: { limit: 5 } }),
    )
    expect(store.recentRecords).toEqual([])
  })

  it('fetchUsuariosConfiguracion passes _suppressErrorToast when falling back to empty list', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useAdminStore()

    await store.fetchUsuariosConfiguracion('')

    expect(api.get).toHaveBeenCalledWith(
      '/api/admin/configuracion/usuarios',
      expect.objectContaining({ _suppressErrorToast: true, params: {} }),
    )
    expect(store.usuariosConfiguracion).toEqual([])
  })
})
