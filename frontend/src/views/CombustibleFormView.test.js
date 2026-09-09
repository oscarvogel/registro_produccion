import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const combustibleStore = vi.hoisted(() => ({
  moviles: [],
  lugaresCarga: [],
  loadingMoviles: false,
  loadingLugares: false,
  saving: false,
  error: null,
  lastCarga: null,
  fetchMoviles: vi.fn().mockResolvedValue([]),
  fetchLugaresCarga: vi.fn().mockResolvedValue([]),
  createCarga: vi.fn(),
}))

vi.mock('@/stores/combustible', () => ({
  useCombustibleStore: () => combustibleStore,
}))

import CombustibleFormView from './CombustibleFormView.vue'

describe('CombustibleFormView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    combustibleStore.fetchMoviles.mockClear()
    combustibleStore.fetchLugaresCarga.mockClear()
    combustibleStore.createCarga.mockClear()
    combustibleStore.error = null
  })

  it('shows field-level validation feedback without submitting an incomplete load', async () => {
    const wrapper = mount(CombustibleFormView, {
      global: {
        stubs: {
          AppIcon: { template: '<span />' },
          PageHeader: { template: '<header><slot name="kicker" /><slot name="actions" /></header>' },
          SectionCard: { template: '<section><slot /></section>' },
        },
        directives: { motionPop: {} },
      },
    })

    await wrapper.get('form').trigger('submit')

    expect(wrapper.text()).toContain('Selecciona un equipo o movil.')
    expect(wrapper.text()).toContain('Ingresa una cantidad de litros mayor a cero.')
    expect(wrapper.text()).toContain('Ingresa el Remito 1.')
    expect(combustibleStore.createCarga).not.toHaveBeenCalled()
    expect(wrapper.find('input[aria-invalid="true"]').exists()).toBe(true)
  })
})
