import { mount } from '@vue/test-utils'
import AnimatedList from './AnimatedList.vue'

describe('AnimatedList', () => {
  it('renders keyed list content with the reusable animation class', () => {
    const wrapper = mount(AnimatedList, {
      slots: {
        default: '<div key="one">Uno</div><div key="two">Dos</div>',
      },
    })

    expect(wrapper.classes()).toContain('app-animated-list')
    expect(wrapper.text()).toContain('Uno')
    expect(wrapper.text()).toContain('Dos')
  })
})
