import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AutocompleteField from './AutocompleteField.vue'

const global = {
  stubs: {
    AppIcon: { template: '<span />' },
  },
  directives: {
    motionPop: {},
  },
}

describe('AutocompleteField', () => {
  it('shows loading, error, empty, and stale states without requiring callers to manage custom markup', async () => {
    const wrapper = mount(AutocompleteField, {
      props: {
        label: 'Operador',
        items: [],
        loading: true,
        error: '',
        stale: true,
        emptyMessage: 'Sin operadores configurados para esta unidad',
        errorMessage: 'No se pudo cargar operadores. Reintentar',
      },
      global,
    })

    expect(wrapper.text()).toContain('Cargando')
    expect(wrapper.text()).toContain('Usando datos guardados en este dispositivo')

    await wrapper.setProps({ loading: false, error: 'No se pudo cargar operadores. Reintentar' })
    expect(wrapper.text()).toContain('No se pudo cargar operadores. Reintentar')

    await wrapper.setProps({ error: '' })
    expect(wrapper.text()).toContain('Sin operadores configurados para esta unidad')
  })
})
