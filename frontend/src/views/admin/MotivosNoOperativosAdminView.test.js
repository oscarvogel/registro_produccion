import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import MotivosNoOperativosAdminView from './MotivosNoOperativosAdminView.vue'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(async (url) => ({ data: url.includes('unidades-negocio') ? [] : [] })),
    post: vi.fn(),
    put: vi.fn(),
  },
}))

describe('MotivosNoOperativosAdminView', () => {
  it('muestra la accion para crear un motivo', () => {
    const wrapper = mount(MotivosNoOperativosAdminView, {
      global: { stubs: { PageHeader: false, SectionCard: false, AppModal: true } },
    })
    expect(wrapper.text()).toContain('Nuevo motivo')
  })
})
