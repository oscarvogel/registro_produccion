import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const state = vi.hoisted(() => ({
  records: [],
  evidencias: [],
  evidenciasToArray: vi.fn(async () => state.evidencias),
  store: null,
  auth: {
    user: { idPersonal: 7, unidad_ids: [], unidad_negocio: null },
    isAdmin: true,
  },
  connectivity: { isBackendUp: true },
  refreshPendingCount: vi.fn().mockResolvedValue(undefined),
  syncPending: vi.fn(),
  toast: { info: vi.fn(), error: vi.fn(), success: vi.fn() },
  deleteRecord: vi.fn().mockResolvedValue(undefined),
  updateRecord: vi.fn().mockResolvedValue(undefined),
  apiPost: vi.fn().mockResolvedValue({ data: {} }),
}))

vi.mock('@/services/api', () => ({ default: { post: state.apiPost } }))
// Se conserva la implementacion real del enrutado por tipo (pendingSubmissionEndpoint
// / stripPendingMetadata) y solo se reemplaza la identidad del registro, que
// escribiria en la base local.
vi.mock('@/services/pendingRecords', async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    ensurePendingIdentity: vi.fn((record) => record.payload),
  }
})
vi.mock('@/services/pendingRecordDetail', () => ({
  buildCaminosProcessGroups: vi.fn(() => []),
}))
vi.mock('@/services/db', () => ({
  default: {
    pendingRecords: {
      orderBy: () => ({ reverse: () => ({ toArray: vi.fn().mockResolvedValue(state.records) }) }),
      delete: state.deleteRecord,
      update: state.updateRecord,
    },
    pendingEvidencias: {
      toArray: state.evidenciasToArray,
    },
  },
}))
vi.mock('@/stores/auth', () => ({ useAuthStore: () => state.auth }))
vi.mock('@/stores/produccion', async () => {
  const { reactive } = await import('vue')
  state.store = reactive({
    pendingCount: 0,
    pendingEvidenceCount: 0,
    refreshPendingCount: state.refreshPendingCount,
    syncPending: state.syncPending,
  })
  return { useProduccionStore: () => state.store }
})
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
    state.evidencias = []
    state.evidenciasToArray.mockClear()
    if (state.store) {
      state.store.pendingCount = 0
      state.store.pendingEvidenceCount = 0
    }
    state.auth.isAdmin = true
    state.refreshPendingCount.mockClear()
    state.deleteRecord.mockClear()
    state.updateRecord.mockClear()
    state.apiPost.mockClear()
    state.apiPost.mockResolvedValue({ data: {} })
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

  it('envia el pendiente de caminos al endpoint de caminos', async () => {
    state.records = [{
      id: 11,
      timestamp: Date.now(),
      payload: {
        UN: 'CAMINOS',
        fecha: '2026-09-12',
        __submission_kind: 'caminos',
      },
      synced: 0,
      syncStatus: 'pending',
    }]

    const wrapper = mount(PendientesView, { global })
    await flushPromises()

    const retryButton = wrapper.findAll('button').find((button) => button.text().includes('Reintentar'))
    expect(retryButton).toBeTruthy()
    expect(retryButton.attributes('disabled')).toBeUndefined()

    await retryButton.trigger('click')
    await flushPromises()

    expect(state.apiPost).toHaveBeenCalledTimes(1)
    expect(state.apiPost.mock.calls[0][0]).toBe('/api/produccion/caminos')
    expect(state.apiPost.mock.calls[0][1]).not.toHaveProperty('__submission_kind')
  })

  it('envia el pendiente de produccion al endpoint de produccion', async () => {
    state.records = [{
      id: 12,
      timestamp: Date.now(),
      payload: { UN: 'CAMINOS', fecha: '2026-09-12' },
      synced: 0,
      syncStatus: 'pending',
    }]

    const wrapper = mount(PendientesView, { global })
    await flushPromises()

    const retryButton = wrapper.findAll('button').find((button) => button.text().includes('Reintentar'))
    expect(retryButton).toBeTruthy()

    await retryButton.trigger('click')
    await flushPromises()

    expect(state.apiPost).toHaveBeenCalledTimes(1)
    expect(state.apiPost.mock.calls[0][0]).toBe('/api/produccion/')
  })

  it('avisa que la foto sigue en el telefono cuando la evidencia todavia no subio', async () => {
    state.records = [{
      id: 21,
      timestamp: Date.now(),
      payload: { UN: 'Demo', form_uuid: 'uuid-21' },
      synced: 0,
      syncStatus: 'pending',
    }]
    state.evidencias = [
      { id: 1, formUuid: 'uuid-21', tipo: 'procesador', synced: 0, syncStatus: 'pending' },
    ]

    const wrapper = mount(PendientesView, { global })
    await flushPromises()

    expect(wrapper.text()).toContain('1 foto(s) adjunta(s), esperando subir')
  })

  it('confirma que la foto ya subio cuando la evidencia esta sincronizada', async () => {
    state.records = [{
      id: 22,
      timestamp: Date.now(),
      payload: { UN: 'Demo', form_uuid: 'uuid-22' },
      synced: 0,
      syncStatus: 'pending',
    }]
    state.evidencias = [
      { id: 2, formUuid: 'uuid-22', tipo: 'procesador', synced: 1, syncStatus: 'synced' },
    ]

    const wrapper = mount(PendientesView, { global })
    await flushPromises()

    expect(wrapper.text()).toContain('Foto subida')
  })

  it('recarga la cola cuando el store sincroniza solo', async () => {
    state.store.pendingCount = 1
    state.store.pendingEvidenceCount = 1
    state.records = [{
      id: 23,
      timestamp: Date.now(),
      payload: { UN: 'Demo', form_uuid: 'uuid-23' },
      synced: 0,
      syncStatus: 'pending',
    }]
    state.evidencias = [
      { id: 3, formUuid: 'uuid-23', tipo: 'procesador', synced: 0, syncStatus: 'pending' },
    ]

    const wrapper = mount(PendientesView, { global })
    await flushPromises()
    expect(wrapper.text()).toContain('1 foto(s) adjunta(s), esperando subir')

    const lecturasAntes = state.evidenciasToArray.mock.calls.length

    // El store sincroniza por su cuenta (evento 'online' o timer de la app):
    // la pantalla tiene que releer la cola en vez de mostrar datos viejos.
    state.store.pendingCount = 0
    state.store.pendingEvidenceCount = 0
    await flushPromises()

    expect(state.evidenciasToArray.mock.calls.length).toBeGreaterThan(lecturasAntes)
  })
})
