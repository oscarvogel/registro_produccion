import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const state = vi.hoisted(() => ({
  records: [],
  auth: {
    user: { idPersonal: 7, unidad_ids: [], unidad_negocio: null },
    isAdmin: true,
  },
  connectivity: { isBackendUp: true },
  refreshPendingCount: vi.fn().mockResolvedValue(undefined),
  syncPending: vi.fn(),
  toast: { info: vi.fn(), error: vi.fn(), success: vi.fn() },
  deleteRecord: vi.fn().mockResolvedValue(undefined),
}))

vi.mock('@/services/api', () => ({ default: { post: vi.fn() } }))
vi.mock('@/services/pendingRecords', () => ({
  ensurePendingIdentity: vi.fn((record) => record.payload),
}))
vi.mock('@/services/pendingRecordDetail', () => ({
  buildCaminosProcessGroups: vi.fn(() => []),
}))
vi.mock('@/services/db', () => ({
  default: {
    pendingRecords: {
      orderBy: () => ({ reverse: () => ({ toArray: vi.fn().mockResolvedValue(state.records) }) }),
      delete: state.deleteRecord,
    },
  },
}))
vi.mock('@/stores/auth', () => ({ useAuthStore: () => state.auth }))
vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => ({
    refreshPendingCount: state.refreshPendingCount,
    syncPending: state.syncPending,
  }),
}))
vi.mock('@/stores/connectivity', () => ({ useConnectivityStore: () => state.connectivity }))
vi.mock('@/stores/toast', () => ({ useToastStore: () => state.toast }))

import PendientesView from './PendientesView.vue'

const global = {
  stubs: {
    AppBadge: { template: '<span><slot /></span>' },
    AppButton: {
      props: ['disabled', 'loading', 'title'],
      template: '<button :disabled="disabled || loading" :title="title"><slot /></button>',
    },
    AppIcon: { template: '<span />' },
    AppModal: {
      props: ['modelValue', 'title', 'description'],
      template: '<div v-if="modelValue" role="dialog"><slot /></div>',
    },
    EmptyState: { props: ['title', 'description'], template: '<div><h3>{{ title }}</h3><p>{{ description }}</p><slot /></div>' },
    MetricCard: {
      props: ['label', 'value', 'description'],
      template: '<article data-testid="metric-card"><span>{{ label }}</span><strong>{{ value }}</strong><small>{{ description }}</small></article>',
    },
    PageHeader: { template: '<header><slot name="kicker" /><slot name="actions" /></header>' },
  },
}

describe('PendientesView', () => {
  beforeEach(() => {
    state.records = []
    state.auth.isAdmin = true
    state.refreshPendingCount.mockClear()
    state.deleteRecord.mockClear()
  })

  it('avoids duplicate local metrics for administrators', async () => {
    const wrapper = mount(PendientesView, { global })
    await flushPromises()

    expect(wrapper.findAll('[data-testid="metric-card"]')).toHaveLength(2)
    expect(wrapper.text()).toContain('Pendientes en este dispositivo')
    expect(wrapper.text()).not.toContain('Pendientes locales')
    expect(wrapper.text()).toContain('Cola vacía')
    expect(wrapper.text()).toContain('Sin actividad reciente de sincronización.')
  })

  it('exposes the selected queue filter to assistive technology', async () => {
    state.records = [{
      id: 1,
      timestamp: Date.now(),
      payload: { UN: 'CAMINOS', fecha: '2026-09-12' },
      synced: 0,
      syncStatus: 'pending',
    }]

    const wrapper = mount(PendientesView, { global })
    await flushPromises()

    const filters = wrapper.findAll('button[aria-pressed]')
    expect(filters).toHaveLength(3)
    expect(filters[0].attributes('aria-pressed')).toBe('true')
    expect(filters[1].attributes('aria-pressed')).toBe('false')
  })
})
