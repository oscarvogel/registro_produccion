import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EvidenciaField from './EvidenciaField.vue'

describe('EvidenciaField', () => {
  it('ofrece el boton para tomar la foto con la camara', () => {
    const wrapper = mount(EvidenciaField, {
      props: { titulo: 'Foto del horometro', ayuda: 'Fotografia el horometro.' },
    })

    expect(wrapper.text()).toContain('Tomar foto')
    expect(wrapper.text()).toContain('Foto del horometro')
    const input = wrapper.find('input[type="file"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('accept')).toBe('image/*')
    expect(input.attributes('capture')).toBe('environment')
  })

  it('marca la foto como obligatoria cuando falta', () => {
    const wrapper = mount(EvidenciaField, {
      props: { titulo: 'Foto del horometro', requerido: true },
    })

    expect(wrapper.text()).toContain('Obligatoria')
  })

  it('muestra la miniatura y el boton Quitar cuando ya hay foto', () => {
    const wrapper = mount(EvidenciaField, {
      props: {
        titulo: 'Foto del horometro',
        requerido: true,
        modelValue: { file: {}, preview: 'blob:preview', nombre: 'foto.jpg' },
      },
    })

    expect(wrapper.find('img').attributes('src')).toBe('blob:preview')
    expect(wrapper.text()).toContain('Rehacer foto')
    expect(wrapper.text()).toContain('Quitar')
    expect(wrapper.text()).toContain('Lista')
  })

  it('emite null cuando se quita la foto', async () => {
    const wrapper = mount(EvidenciaField, {
      props: {
        titulo: 'Foto del horometro',
        modelValue: { file: {}, preview: 'blob:preview', nombre: 'foto.jpg' },
      },
    })

    const botones = wrapper.findAll('button')
    await botones[botones.length - 1].trigger('click')

    expect(wrapper.emitted('update:modelValue')).toEqual([[null]])
  })

  it('muestra el subtexto (la lectura que hay que documentar)', () => {
    const wrapper = mount(EvidenciaField, {
      props: { titulo: 'Foto del horometro', subtexto: 'Documenta la lectura final: 1850.5.' },
    })

    expect(wrapper.text()).toContain('Documenta la lectura final: 1850.5.')
  })
})
