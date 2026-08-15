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

    expect(wrapper.text()).toContain('No se pudieron cargar los datos necesarios. Actualiza e intenta nuevamente.')
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

  it('exposes a multi-unit Relaciones tab when editing a movil', async () => {
    routeState.params.entity = 'moviles'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/moviles': [
          { idMovil: 7, patente: 'MWY673', detalle: 'Transporte Forestal', id_unidad_negocio: 3, unidad_ids: [3, 5], activo: 1 },
        ],
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 3, nombre: 'COSECHA CTL', prefijo: 'CTL', activo: 1 },
          { idUnidadNegocio: 5, nombre: 'TALLER', prefijo: 'TAL', activo: 1 },
        ],
        '/api/admin/tipos-proceso': [],
        '/api/admin/tipos-movil': [],
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

    const editar = wrapper.findAll('button').find((button) => button.text().includes('Editar') || button.text().includes('Edit'))
    // si no hay "Editar", abrir el form con Nuevo
    const trigger = editar || wrapper.findAll('button').find((button) => button.text().includes('Nuevo'))
    expect(trigger).toBeTruthy()
    await trigger.trigger('click')
    await flushPromises()

    const relaciones = wrapper.findAll('button').find((button) => button.text().trim() === 'Relaciones')
    expect(relaciones).toBeTruthy()
    await relaciones.trigger('click')
    await flushPromises()

    const labels = wrapper.findAll('label').map((label) => label.text())
    expect(labels).toContain('Unidad Principal')
    expect(labels).toContain('Unidades vinculadas')
  })


  it('honors unidad_ids when filtering moviles available for a business unit', async () => {
    routeState.params.entity = 'unidades-negocio'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 1, nombre: 'COSECHA DELTA', prefijo: 'DELTA', activo: 1 },
          { idUnidadNegocio: 2, nombre: 'TALLER', prefijo: 'TAL', activo: 1 },
        ],
        '/api/admin/personal': [],
        '/api/admin/moviles': [
          { idMovil: 12, patente: 'ZZZ999', detalle: 'Zorra Forestal', id_unidad_negocio: 2, unidad_ids: [2] },
          { idMovil: 10, patente: 'AAA111', detalle: 'Carreton Multi', id_unidad_negocio: 1, unidad_ids: [1, 2] },
          { idMovil: 11, patente: 'BBB222', detalle: 'Solo Delta', id_unidad_negocio: 1, unidad_ids: [1] },
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
    await relaciones.trigger('click')
    await flushPromises()

    // Relacionados a la unidad 1: solo "Carreton Multi" (porque esta en [1, 2])
    // y "Solo Delta" (porque esta en [1]).
    const wrapperText = wrapper.text()
    expect(wrapperText).toContain('AAA111 - Carreton Multi')
    expect(wrapperText).toContain('BBB222 - Solo Delta')
    expect(wrapperText).not.toContain('ZZZ999 - Zorra Forestal')

    const agregarMovil = wrapper.findAll('button[title="Agregar Moviles"]').at(0)
    await agregarMovil.trigger('click')
    await flushPromises()

    const input = wrapper.find('input[role="combobox"]')
    await input.trigger('focus')
    await flushPromises()
    const optionLabels = wrapper.findAll('[role="option"]').map((option) => option.text())
    expect(optionLabels).toEqual(['ZZZ999 - Zorra Forestal'])
  })

  it('replaces the unit when moving a vehicle from one business unit to another (#142)', async () => {
    routeState.params.entity = 'unidades-negocio'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 1, nombre: 'Caminos', prefijo: 'CAM', activo: 1 },
          { idUnidadNegocio: 2, nombre: 'Sin detalle', prefijo: 'SD', activo: 1 },
        ],
        '/api/admin/personal': [],
        '/api/admin/moviles': [
          { idMovil: 10, patente: 'AAA111', detalle: 'Motoniveladora', id_unidad_negocio: 1, unidad_ids: [1] },
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

    // 1. Open Relaciones for the first business unit (Caminos)
    const relaciones = wrapper.findAll('button').find((b) => b.text().includes('Relaciones'))
    expect(relaciones).toBeTruthy()
    await relaciones.trigger('click')
    await flushPromises()

    // 2. The Mover action button on the movile should be reachable by its title
    const moverButtons = wrapper.findAll('button[title="Mover AAA111 - Motoniveladora"]')
    expect(moverButtons.length).toBeGreaterThan(0)
    await moverButtons[0].trigger('click')
    await flushPromises()

    // 3. The move form exposes a select with the placeholder "Mover a unidad"
    const moveSelect = wrapper.findAll('select').find((s) => {
      const opts = s.findAll('option').map((o) => o.text())
      return opts.includes('Mover a unidad')
    })
    expect(moveSelect).toBeTruthy()

    // 4. Pick the Sin detalle unit (idUnidadNegocio = 2)
    await moveSelect.setValue(2)
    await flushPromises()

    // 5. The save button inside the move form is the one with class bg-primary inside the same flex container
    // It is uniquely identified by being the first button in a flex container that also contains a select with the move placeholder.
    const moveFormButton = wrapper.findAll('div.mb-2.flex.gap-2 > button.bg-primary').find((b) => {
      const parent = b.element.parentElement
      if (!parent) return false
      return parent.querySelector('select') !== null
    })
    expect(moveFormButton).toBeTruthy()
    await moveFormButton.trigger('click')
    await flushPromises()

    // 6. The payload sent to the backend must replace the unit, not append to it
    expect(api.put).toHaveBeenCalledWith('/api/admin/moviles/10', { unidad_ids: [2] })

    // 7. The original unit must NOT be present in the payload
    expect(api.put).not.toHaveBeenCalledWith(
      '/api/admin/moviles/10',
      expect.objectContaining({
        unidad_ids: expect.arrayContaining([1]),
      }),
    )
  })

  it('exposes a multi-unit selector for lugares de carga and lists every linked unit', async () => {
    routeState.params.entity = 'lugares-carga'
    api.get.mockImplementation((url) => {
      const dataByUrl = {
        '/api/admin/lugares-carga': [
          {
            idLugarCarga: 9,
            detalle: 'BASE FG - STOCK COMBUSTIBLE',
            unidad_negocio: 1,
            unidad_ids: [1, 2],
            activo: 1,
          },
        ],
        '/api/admin/unidades-negocio': [
          { idUnidadNegocio: 1, nombre: 'STOCK DE COMBUSTIBLE - BASE FG', prefijo: 'STK', activo: 1 },
          { idUnidadNegocio: 2, nombre: 'COSECHA DELTA', prefijo: 'DEL', activo: 1 },
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

    expect(wrapper.text()).toContain('STOCK DE COMBUSTIBLE - BASE FG')
    expect(wrapper.text()).toContain('COSECHA DELTA')

    const nuevo = wrapper.findAll('button').find((button) => button.text().includes('Nuevo'))
    expect(nuevo).toBeTruthy()
    await nuevo.trigger('click')
    await flushPromises()

    const labels = wrapper.findAll('label').map((label) => label.text())
    expect(labels).toContain('Unidades de Negocio')
    const unitCheckboxes = wrapper.findAll('.app-surface-muted input[type="checkbox"]')
    expect(unitCheckboxes.length).toBe(2)
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
