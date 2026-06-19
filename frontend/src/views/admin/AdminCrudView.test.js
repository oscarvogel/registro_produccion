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
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}))

import api from '@/services/api'
import AdminCrudView from './AdminCrudView.vue'

describe('AdminCrudView tipos de proceso', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    api.get.mockResolvedValue({ data: [] })
    api.post.mockResolvedValue({ data: {} })
    api.put.mockResolvedValue({ data: {} })
    api.delete.mockResolvedValue({ data: {} })
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

  it('shows a friendly message instead of raw SQL when saving fails', async () => {
    api.post.mockRejectedValueOnce({
      response: {
        status: 503,
        data: {
          detail: "(pymysql.err.OperationalError) (2013, 'Lost connection to MySQL server during query') [SQL: SELECT personal.`idPersonal` FROM personal WHERE personal.`idPersonal` = %(idPersonal_1)s]",
        },
      },
    })

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
    await nuevo.trigger('click')

    const nombre = wrapper.findAll('input[type="text"]').at(1)
    await nombre.setValue('Trabajos Eventuales')

    const guardar = wrapper.findAll('button').find((button) => button.text().includes('Guardar'))
    await guardar.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('No se pudieron cargar los datos necesarios. Actualiza e intenta nuevamente.')
    expect(wrapper.text()).not.toContain('SELECT personal')
    expect(wrapper.text()).not.toContain('OperationalError')
    expect(wrapper.text()).not.toContain('Lost connection')
  })
})
