import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import InputField from './InputField.vue'

describe('InputField', () => {
  it('keeps numeric controls decimal-friendly', () => {
    const wrapper = mount(InputField, {
      props: {
        type: 'number',
        min: 1,
        step: 'any',
        modelValue: 4382.4,
      },
    })

    const input = wrapper.get('input')

    expect(input.attributes('type')).toBe('text')
    expect(input.attributes('inputmode')).toBe('decimal')
    expect(input.attributes('min')).toBe('1')
    expect(input.attributes('step')).toBe('any')
  })

  it('normalizes decimal commas before updating numeric models', async () => {
    const wrapper = mount(InputField, {
      props: {
        type: 'number',
        modelValue: '',
      },
    })

    await wrapper.get('input').setValue('4382,4')

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['4382.4'])
  })
})
