import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AppButton from './AppButton.vue'


describe('AppButton', () => {
  it('disables the button while loading and keeps the label visible', () => {
    const wrapper = mount(AppButton, {
      props: { loading: true },
      slots: { default: 'Guardar' },
    })

    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Guardar')
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })
})
