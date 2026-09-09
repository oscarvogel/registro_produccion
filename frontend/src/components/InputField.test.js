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

  it('associates an invalid field with its visible error', () => {
    const wrapper = mount(InputField, {
      props: {
        id: 'litros',
        label: 'Litros',
        invalid: true,
        errorMessage: 'Ingresá una cantidad válida.',
      },
    })

    const input = wrapper.get('input')
    expect(wrapper.get('label').attributes('for')).toBe('litros')
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(input.attributes('aria-describedby')).toBe('litros-error')
    expect(wrapper.get('#litros-error').text()).toContain('Ingresá una cantidad válida.')
  })
})
