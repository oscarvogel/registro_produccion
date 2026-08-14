import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const state = vi.hoisted(() => ({
  onAction: null,
  unsubscribe: vi.fn(),
  store: {
    unidadesNegocio: [
      { idUnidadNegocio: 1, nombre: 'BIOMASA LAS MARIAS' },
      { idUnidadNegocio: 9, nombre: 'Caminos' },
    ],
    $onAction: vi.fn((callback) => {
      state.onAction = callback
      return state.unsubscribe
    }),
  },
}))

vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => state.store,
}))

import ProduccionFormView from './ProduccionFormView.vue'

const global = {
  stubs: {
    ProduccionLegacyFormView: {
      template: '<div data-testid="legacy-form">FORMULARIO HABITUAL</div>',
    },
    CaminosFormView: {
      props: ['unidad'],
      emits: ['back'],
      template: '<div data-testid="caminos-form">CAMINOS {{ unidad.nombre }}<button data-testid="back" @click="$emit(\'back\')">volver</button></div>',
    },
  },
}

describe('ProduccionFormView', () => {
  it('entra directamente al formulario habitual y solo cambia de modo al seleccionar Caminos', async () => {
    const wrapper = mount(ProduccionFormView, { global })

    expect(wrapper.find('[data-testid="legacy-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="caminos-form"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('¿Para qué unidad vas a cargar?')

    state.onAction({ name: 'fetchTiposProceso', args: [1] })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-testid="legacy-form"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="caminos-form"]').exists()).toBe(false)

    state.onAction({ name: 'fetchTiposProceso', args: [9] })
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-testid="legacy-form"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="caminos-form"]').exists()).toBe(true)

    await wrapper.get('[data-testid="back"]').trigger('click')
    expect(wrapper.find('[data-testid="legacy-form"]').exists()).toBe(true)
  })
})
