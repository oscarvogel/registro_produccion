import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import FeedbackMessage from './FeedbackMessage.vue'

describe('FeedbackMessage', () => {
  it('exposes loading as a polite status', () => {
    const wrapper = mount(FeedbackMessage, {
      props: { tone: 'loading', message: 'Cargando datos...' },
      global: { stubs: { AppIcon: { template: '<span />' } } },
    })

    expect(wrapper.attributes('role')).toBe('status')
    expect(wrapper.attributes('aria-live')).toBe('polite')
    expect(wrapper.attributes('aria-busy')).toBe('true')
  })

  it('announces errors assertively', () => {
    const wrapper = mount(FeedbackMessage, {
      props: { tone: 'error', message: 'No se pudo guardar.' },
      global: { stubs: { AppIcon: { template: '<span />' } } },
    })

    expect(wrapper.attributes('role')).toBe('alert')
    expect(wrapper.attributes('aria-live')).toBe('assertive')
  })
})
