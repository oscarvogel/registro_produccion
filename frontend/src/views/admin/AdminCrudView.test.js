import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const routeState = vi.hoisted(() => ({
  params: { entity: 'tipos-proceso' },
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => ({ replace: vi.fn() }),
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
  getUserSafeErrorMessage: vi.fn((_err, fallback) => fallback),
}))

import api from '@/services/api'
import AdminCrudView from './AdminCrudView.vue'

describe('AdminCrudView tipos de proceso', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    routeState.params.entity = 'tipos-proceso'
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

    expect(wrapper.text()).toContain('No se pudo guardar el registro. Actualiza e intenta nuevamente.')
    expect(wrapper.text()).not.toContain('SELECT personal')
    expect(wrapper.text()).not.toContain('OperationalError')
    expect(wrapper.text()).not.toContain('Lost connection')
  })

  it('uses a searchable sorted autocomplete when adding personal to a business unit', async () => {
    routeState.params.entity = 'unidades-negocio'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 1, nombre: 'COSECHA DELTA', prefijo: 'DELTA', activo: 1 },
          { idUnidadNegocio: 2, nombre: 'TALLER', prefijo: 'TAL', activo: 1 },
        ],
        '/api/admin/personal': [
          { idPersonal: 8, nombre: 'Zulu Operador', dni: '303', unidad_ids: [] },
          { idPersonal: 7, nombre: 'Ana Alvarez', dni: '101', unidad_ids: [] },
          { idPersonal: 9, nombre: 'Marcado Actual', dni: '909', unidad_ids: [1] },
        ],
        '/api/admin/moviles': [],
        '/api/admin/tipos-proceso': [],
      }
      return Promise.resolve({ data: dataByUrl[url] || [] })
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

    const relaciones = wrapper.findAll('button').find((button) => button.text().includes('Relaciones'))
    expect(relaciones).toBeTruthy()
    await relaciones.trigger('click')
    await flushPromises()

    const agregarPersonal = wrapper.findAll('button[title="Agregar Personal"]').at(0)
    expect(agregarPersonal).toBeTruthy()
    await agregarPersonal.trigger('click')
    await flushPromises()

    const input = wrapper.find('input[role="combobox"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Buscar personal')

    await input.trigger('focus')
    await flushPromises()
    const optionLabels = wrapper.findAll('[role="option"]').map((option) => option.text())
    expect(optionLabels.slice(0, 2)).toEqual(['Ana Alvarez - DNI 101', 'Zulu Operador - DNI 303'])

    await input.setValue('101')
    await flushPromises()
    expect(wrapper.findAll('[role="option"]').map((option) => option.text())).toEqual(['Ana Alvarez - DNI 101'])
  })

  it('uses a searchable sorted autocomplete when adding a vehicle to a business unit', async () => {
    routeState.params.entity = 'unidades-negocio'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 1, nombre: 'COSECHA DELTA', prefijo: 'DELTA', activo: 1 },
        ],
        '/api/admin/personal': [],
        '/api/admin/moviles': [
          { idMovil: 12, patente: 'ZZZ999', detalle: 'Zorra Forestal', id_unidad_negocio: 2 },
          { idMovil: 10, patente: 'AAA111', detalle: 'Carreton Principal', id_unidad_negocio: 2 },
          { idMovil: 11, patente: 'BBB222', detalle: 'Ya vinculado', id_unidad_negocio: 1 },
        ],
        '/api/admin/tipos-proceso': [],
      }
      return Promise.resolve({ data: dataByUrl[url] || [] })
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

    const relaciones = wrapper.findAll('button').find((button) => button.text().includes('Relaciones'))
    expect(relaciones).toBeTruthy()
    await relaciones.trigger('click')
    await flushPromises()

    const agregarMovil = wrapper.findAll('button[title="Agregar Moviles"]').at(0)
    expect(agregarMovil).toBeTruthy()
    await agregarMovil.trigger('click')
    await flushPromises()

    const input = wrapper.find('input[role="combobox"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Buscar movil')

    await input.trigger('focus')
    await flushPromises()
    expect(wrapper.findAll('[role="option"]').map((option) => option.text())).toEqual([
      'AAA111 - Carreton Principal',
      'ZZZ999 - Zorra Forestal',
    ])

    await input.setValue('carreton')
    await flushPromises()
    expect(wrapper.findAll('[role="option"]').map((option) => option.text())).toEqual(['AAA111 - Carreton Principal'])
  })

  it('keeps two business units selected and sends both when saving a person', async () => {
    routeState.params.entity = 'personal'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/personal': [
          {
            idPersonal: 5,
            nombre: 'Ana Alvarez',
            dni: '30111222',
            cuit: '',
            id_puesto: 1,
            unidad_negocio: 1,
            unidad_ids: [1],
            tipo_de_proceso_id: null,
            entrada_m: '00:00',
            salida_m: '00:00',
            entrada_t: '00:00',
            salida_t: '00:00',
            telefono: '',
            domicilio: '',
            activo: 1,
            encargado: 0,
            is_admin: 0,
          },
        ],
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 2, nombre: 'TALLER', prefijo: 'TAL', activo: 1 },
          { idUnidadNegocio: 1, nombre: 'COSECHA DELTA', prefijo: 'DELTA', activo: 1 },
        ],
        '/api/admin/tipos-proceso': [],
      }
      return Promise.resolve({ data: dataByUrl[url] || [] })
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

    const editar = wrapper.findAll('button').find((button) => button.text() === 'Editar')
    expect(editar).toBeTruthy()
    await editar.trigger('click')

    const relaciones = wrapper.findAll('button').find((button) => button.text() === 'Relaciones')
    expect(relaciones).toBeTruthy()
    await relaciones.trigger('click')

    const unitLabels = wrapper.findAll('label').filter((label) => ['COSECHA DELTA', 'TALLER'].includes(label.text()))
    expect(unitLabels.map((label) => label.text())).toEqual(['COSECHA DELTA', 'TALLER'])

    const deltaCheckbox = unitLabels[0].get('input[type="checkbox"]')
    const tallerCheckbox = unitLabels[1].get('input[type="checkbox"]')
    expect(deltaCheckbox.element.checked).toBe(true)
    expect(tallerCheckbox.element.checked).toBe(false)

    await tallerCheckbox.setValue(true)
    expect(deltaCheckbox.element.checked).toBe(true)
    expect(tallerCheckbox.element.checked).toBe(true)
    expect(wrapper.text()).toContain('2 seleccionadas')

    const guardar = wrapper.findAll('button').find((button) => button.text().includes('Guardar'))
    await guardar.trigger('click')
    await flushPromises()

    expect(api.put).toHaveBeenCalledWith(
      '/api/admin/personal/5',
      expect.objectContaining({
        unidad_negocio: 1,
        unidad_ids: [1, 2],
      }),
    )
  })

  it('shows an admin CRUD form for actas used by the production combo', async () => {
    routeState.params.entity = 'actas'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/actas': [
          { id: 3, numero: '7900000099', rodal_id: 12, periodo: '202607', vam: 1, tarifa: 2, extraccion: 3, carga: 4 },
        ],
        '/api/admin/rodales': [
          { idRodal: 12, rodal: 'Rodal 12', idPredio: 5, vam: 1, tarifa: 2, extraccion: 3, carga: 4 },
        ],
      }
      return Promise.resolve({ data: dataByUrl[url] || [] })
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

    expect(wrapper.text()).toContain('Actas')
    expect(wrapper.text()).toContain('7900000099')

    const nuevo = wrapper.findAll('button').find((button) => button.text().includes('Nuevo'))
    expect(nuevo).toBeTruthy()
    await nuevo.trigger('click')
    await flushPromises()

    const labels = wrapper.findAll('label').map((label) => label.text())
    expect(labels).toContain('Número')
    expect(labels).toContain('Rodal')
    expect(labels).toContain('Periodo')
    expect(labels).toContain('VAM')
    expect(labels).toContain('Tarifa')
    expect(labels).toContain('Extracción')
    expect(labels).toContain('Carga')
  })
})
