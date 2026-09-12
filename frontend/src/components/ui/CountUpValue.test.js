import { mount } from '@vue/test-utils'
import CountUpValue from './CountUpValue.vue'

describe('CountUpValue', () => {
  it('formats the target value immediately when reduced motion is preferred', async () => {
    const originalMatchMedia = window.matchMedia
    window.matchMedia = () => ({ matches: true })

    const wrapper = mount(CountUpValue, {
      props: {
        value: 1234.5,
        from: 0,
        format: (value) => Number(value).toFixed(1),
      },
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toBe('1234.5')

    window.matchMedia = originalMatchMedia
  })
})
