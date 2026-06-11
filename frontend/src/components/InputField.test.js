import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import InputField from './InputField.vue'

describe('InputField', () => {
  it('passes numeric step constraints to the native input', () => {
    const wrapper = mount(InputField, {
      props: {
        type: 'number',
        min: 1,
        step: 'any',
        modelValue: 4382.4,
      },
    })

    const input = wrapper.get('input')

    expect(input.attributes('type')).toBe('number')
    expect(input.attributes('min')).toBe('1')
    expect(input.attributes('step')).toBe('any')
  })
})
