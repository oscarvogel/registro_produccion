import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'

const push = vi.fn()
const store = {
  operadores: [],
  moviles: [],
  tiposProceso: [
    { id: 9, nombre: 'PERFILADO' },
    { id: 20, nombre: 'DISPOSICION' },
    { id: 21, nombre: 'REMOLQUE' },
  ],
  predios: [],
  actas: [],
  rodales: [],
  lugaresCarga: [],
  submitting: false,
  error: null,
  fetchTiposProceso: vi.fn(async () => []),
  fetchMoviles: vi.fn(async () => []),
  fetchLugaresCarga: vi.fn(async () => []),
  fetchPredios: vi.fn(async () => []),
  fetchActas: vi.fn(async () => []),
  fetchRodales: vi.fn(async () => []),
  fetchRodalesPorActa: vi.fn(async () => []),
  fetchOperadores: vi.fn(async () => []),
  submitParteCaminos: vi.fn(),
}

vi.mock('vue-router', () => ({
  useRouter: () => ({ push }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAdmin: false,
    userName: 'Operador Prueba',
    user: { idPersonal: 44, encargado: 0 },
  }),
}))

vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => store,
}))

import AutocompleteField from '@/components/AutocompleteField.vue'
import motivosNoOperativos from '@/data/motivosNoOperativos.json'
import CaminosFormView from './CaminosFormView.vue'

function mountView() {
  return mount(CaminosFormView, {
    props: {
      unidad: { idUnidadNegocio: 7, nombre: 'Caminos' },
    },
    global: {
      stubs: {
        SectionCard: {
          props: ['title'],
          template: '<section><h2>{{ title }}</h2><slot /></section>',
        },
        InputField: {
          props: ['label', 'modelValue'],
          emits: ['update:modelValue'],
          template: '<label><span>{{ label }}</span><input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" /></label>',
        },
      },
    },
  })
}

describe('CaminosFormView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('allows adding and removing process rows in the same daily part', async () => {
    const wrapper = mountView()

    expect(wrapper.text()).toContain('Proceso 1')
    expect(wrapper.text()).not.toContain('Proceso 2')

    const addButton = wrapper.findAll('button').find((button) => button.text().includes('Agregar proceso'))
    expect(addButton).toBeTruthy()
    await addButton.trigger('click')

    expect(wrapper.text()).toContain('Proceso 1')
    expect(wrapper.text()).toContain('Proceso 2')

    const removeButton = wrapper.findAll('button').find((button) => button.text().trim() === 'Quitar')
    expect(removeButton).toBeTruthy()
    await removeButton.trigger('click')

    expect(wrapper.text()).toContain('Proceso 1')
    expect(wrapper.text()).not.toContain('Proceso 2')
  })

  it('uses the shared non-operational reason catalog', async () => {
    const wrapper = mountView()

    wrapper.vm.form.hrs_no_op = 2
    wrapper.vm.pasoActual = 4
    await nextTick()

    const reasonField = wrapper.findAllComponents(AutocompleteField).find(
      (component) => component.props('label') === 'Motivo no operativo',
    )

    expect(reasonField).toBeTruthy()
    expect(reasonField.props('items')).toEqual(motivosNoOperativos)
    expect(reasonField.props('disabled')).toBe(false)

    wrapper.vm.form.motivo_no_op = 'FALLA MECANICA'
    wrapper.vm.form.hrs_no_op = 0
    await nextTick()
    expect(wrapper.vm.form.motivo_no_op).toBe('')
  })

  it('blocks production when disposition plus towing exceeds available shift hours', async () => {
    const wrapper = mountView()

    wrapper.vm.form.hr_inicio = 1
    wrapper.vm.form.hr_fin = 15
    wrapper.vm.form.hrs_no_op = 0
    wrapper.vm.procesos[0].tipo_proceso_id = 20
    wrapper.vm.procesos[0].predio_id = 1
    wrapper.vm.procesos[0].hr_disposicion = 12
    wrapper.vm.agregarProceso()
    wrapper.vm.procesos[1].tipo_proceso_id = 21
    wrapper.vm.procesos[1].predio_id = 1
    wrapper.vm.procesos[1].hr_remolque = 5
    wrapper.vm.pasoActual = 5
    await nextTick()

    expect(wrapper.vm.horasOperativasDisponibles).toBe(14)
    expect(wrapper.vm.totalHorasProcesos).toBe(17)
    expect(wrapper.vm.horasProcesosValidas).toBe(false)
    expect(wrapper.vm.puedeAvanzar).toBe(false)
    expect(wrapper.text()).toContain('17 h de 14 h disponibles')
    expect(wrapper.text()).toContain('Reducí las horas de disposición/remolque')
  })

  it('loads Caminos-scoped catalogs when mounted', async () => {
    mountView()

    await Promise.resolve()
    expect(store.fetchTiposProceso).toHaveBeenCalledWith(7)
    expect(store.fetchMoviles).toHaveBeenCalledWith(7)
    expect(store.fetchLugaresCarga).toHaveBeenCalledWith(7)
  })
})
