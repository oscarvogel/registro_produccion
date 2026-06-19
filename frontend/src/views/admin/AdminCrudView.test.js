import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { entity: 'tipos-proceso' } }),
  useRouter: () => ({ replace: vi.fn() }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import AdminCrudView from './AdminCrudView.vue'

describe('AdminCrudView tipos de proceso', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: [] })
  })

  it('shows configurable Acta, Predio, and Rodal requirements in the process type form', async () => {
    const wrapper = mount(AdminCrudView, {
      global: {
        directives: {
          motionPanel: {},
          motionPop: {},
        },
        stubs: {
          AppIcon: true,
        },
      },
    })
    await flushPromises()

    const nuevo = wrapper.findAll('button').find((button) => button.text().includes('Nuevo'))
    expect(nuevo).toBeTruthy()
    await nuevo.trigger('click')

    const requisitos = wrapper.findAll('button').find((button) => button.text() === 'Requisitos')
    expect(requisitos).toBeTruthy()
    await requisitos.trigger('click')

    const labels = wrapper.findAll('label').map((label) => label.text())
    expect(labels).toContain('Requiere Acta')
    expect(labels).toContain('Requiere Predio')
    expect(labels).toContain('Requiere Rodal')
  })
})
