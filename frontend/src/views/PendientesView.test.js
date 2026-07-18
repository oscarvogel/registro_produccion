import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

const mocks = vi.hoisted(() => ({
  syncPending: vi.fn(),
  refreshPendingCount: vi.fn(),
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
  records: [],
}))

vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => ({
    syncPending: mocks.syncPending,
    refreshPendingCount: mocks.refreshPendingCount,
  }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAdmin: true,
    user: { idPersonal: 1, encargado: 0, unidad_ids: [] },
  }),
}))

vi.mock('@/stores/toast', () => ({
  useToastStore: () => ({
    success: mocks.success,
    error: mocks.error,
    info: mocks.info,
  }),
}))

vi.mock('@/services/db', () => ({
  default: {
    pendingRecords: {
      orderBy: () => ({
        reverse: () => ({
          toArray: async () => [...mocks.records],
        }),
      }),
      delete: vi.fn(),
      update: vi.fn(),
    },
  },
}))

vi.mock('@/services/api', () => ({
  default: { post: vi.fn() },
  getUserSafeErrorMessage: (_error, fallback) => fallback,
}))

import PendientesView from './PendientesView.vue'

describe('PendientesView bulk synchronization feedback', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    mocks.records.splice(0, mocks.records.length)
  })

  it('reports a partial result instead of complete success when records remain pending', async () => {
    mocks.records.push({
      id: 1,
      timestamp: Date.now(),
      synced: 0,
      syncStatus: 'pending',
      payload: { cod_operador: 1 },
    })
    mocks.syncPending.mockResolvedValue({
      successCount: 2,
      permanentFailureCount: 0,
      transientFailureCount: 1,
    })

    const wrapper = mount(PendientesView, {
      global: {
        stubs: {
          AppBadge: true,
          AppButton: {
            template: '<button type="button" @click="$emit(\'click\')"><slot /></button>',
          },
          AppIcon: true,
          AppModal: true,
          EmptyState: true,
          MetricCard: true,
          PageHeader: {
            template: '<div><slot name="actions" /></div>',
          },
        },
      },
    })

    await vi.waitFor(() => expect(mocks.refreshPendingCount).toHaveBeenCalled())
    const syncButton = wrapper.findAll('button').find((button) => button.text().includes('Sincronizar'))
    await syncButton.trigger('click')
    await vi.waitFor(() => expect(mocks.syncPending).toHaveBeenCalled())

    expect(mocks.success).not.toHaveBeenCalled()
    expect(mocks.error).not.toHaveBeenCalled()
  })
})
