import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AdminCenterView from './AdminCenterView.vue'

describe('AdminCenterView', () => {
  it('groups every existing administrative destination in the center', () => {
    const wrapper = mount(AdminCenterView, {
      global: {
        directives: { motionPanel: {} },
        stubs: {
          AppIcon: true,
          RouterLink: {
            props: ['to'],
            template: '<a :data-route="to.name" :data-entity="to.params?.entity"><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Personas y equipos')
    expect(wrapper.text()).toContain('Configuración productiva')
    expect(wrapper.text()).toContain('Seguridad')

    const entityLinks = wrapper.findAll('[data-route="admin-crud"]')
    expect(entityLinks.map((link) => link.attributes('data-entity'))).toEqual([
      'personal',
      'moviles',
      'asignaciones',
      'unidades-negocio',
      'tipos-proceso',
      'lugares-carga',
      'predios',
      'rodales',
      'actas',
    ])
    expect(wrapper.findAll('[data-route="admin-configuracion"]')).toHaveLength(1)
  })
})
