import { mount } from '@vue/test-utils'
import RevealStagger from './RevealStagger.vue'

describe('RevealStagger', () => {
  it('renders its slot and reveals immediately when IntersectionObserver is unavailable', async () => {
    const wrapper = mount(RevealStagger, {
      slots: { default: '<span>Contenido</span>' },
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Contenido')
    expect(wrapper.classes()).toContain('app-reveal-stagger--visible')
  })
})
