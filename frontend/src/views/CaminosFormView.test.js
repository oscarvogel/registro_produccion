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
    userName: '  Operador Prueba  ',
    user: { idPersonal: 44, encargado: 0 },
  }),
}))

vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => store,
}))

import AutocompleteField from '@/components/AutocompleteField.vue'
import motivosNoOperativos from '@/data/motivosNoOperativos.json'
import CaminosFormView from './CaminosFormView.vue'

function mountView(unidad = { idUnidadNegocio: 7, nombre: 'Caminos' }) {
  return mount(CaminosFormView, {
    props: {
      unidad,
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

  it('allows disposition hours over meter difference when towing remains valid', async () => {
    const wrapper = mountView()

    wrapper.vm.form.hr_inicio = 1
    wrapper.vm.form.hr_fin = 15
    wrapper.vm.form.hrs_no_op = 4
    wrapper.vm.form.motivo_no_op = 'Reparacion'
    wrapper.vm.procesos[0].tipo_proceso_id = 20
    wrapper.vm.procesos[0].predio_id = 1
    wrapper.vm.procesos[0].hr_disposicion = 20
    wrapper.vm.agregarProceso()
    wrapper.vm.procesos[1].tipo_proceso_id = 21
    wrapper.vm.procesos[1].predio_id = 1
    wrapper.vm.procesos[1].hr_remolque = 14
    wrapper.vm.pasoActual = 5
    await nextTick()

    expect(wrapper.vm.horasJornada).toBe(14)
    expect(wrapper.vm.totalHorasRemolque).toBe(14)
    expect(wrapper.vm.horasRemolqueValidas).toBe(true)
    expect(wrapper.vm.puedeAvanzar).toBe(true)
    expect(wrapper.text()).toContain('Horas de remolque: 14 h de 14 h')
    expect(wrapper.text()).not.toContain('disposición/remolque')
  })

  it('blocks production only when towing exceeds meter difference', async () => {
    const wrapper = mountView()

    wrapper.vm.form.hr_inicio = 1
    wrapper.vm.form.hr_fin = 4
    wrapper.vm.procesos[0].tipo_proceso_id = 20
    wrapper.vm.procesos[0].predio_id = 1
    wrapper.vm.procesos[0].hr_disposicion = 20
    wrapper.vm.agregarProceso()
    wrapper.vm.procesos[1].tipo_proceso_id = 21
    wrapper.vm.procesos[1].predio_id = 1
    wrapper.vm.procesos[1].hr_remolque = 4
    wrapper.vm.pasoActual = 5
    await nextTick()

    expect(wrapper.vm.horasJornada).toBe(3)
    expect(wrapper.vm.totalHorasRemolque).toBe(4)
    expect(wrapper.vm.horasRemolqueValidas).toBe(false)
    expect(wrapper.vm.puedeAvanzar).toBe(false)
    expect(wrapper.text()).toContain('Horas de remolque: 4 h de 3 h')
    expect(wrapper.text()).toContain('Reducí las horas de remolque')
  })

  it('sends a trimmed two-process payload without concatenating operations', async () => {
    store.moviles = [{ idMovil: 10, detalle: '  FORWA-N°2  ', patente: '  PAT-001  ' }]
    store.predios = [{ idPredio: 1, nombre: '  PUERTO BOSSETTI  ' }]
    const wrapper = mountView({ idUnidadNegocio: 7, nombre: '  Caminos  ' })

    wrapper.vm.form.fecha = '2026-08-14'
    wrapper.vm.form.cod_equipo = 10
    wrapper.vm.form.hr_inicio = 1
    wrapper.vm.form.hr_fin = 20
    wrapper.vm.form.observaciones = '  parte con dos procesos  '
    wrapper.vm.procesos[0].tipo_proceso_id = 20
    wrapper.vm.procesos[0].predio_id = 1
    wrapper.vm.procesos[0].hr_disposicion = 12
    wrapper.vm.agregarProceso()
    wrapper.vm.procesos[1].tipo_proceso_id = 21
    wrapper.vm.procesos[1].predio_id = 1
    wrapper.vm.procesos[1].hr_remolque = 5
    wrapper.vm.pasoActual = 8

    await wrapper.vm.guardar()

    expect(store.submitParteCaminos).toHaveBeenCalledTimes(1)
    const payload = store.submitParteCaminos.mock.calls[0][0]
    expect(payload).toMatchObject({
      UN: 'Caminos',
      equipo: 'FORWA-N°2 - PAT-001',
      operador: 'Operador Prueba',
      observaciones: 'parte con dos procesos',
    })
    expect(Array.isArray(payload.procesos)).toBe(true)
    expect(payload.procesos).toHaveLength(2)
    expect(payload.procesos).toEqual([
      expect.objectContaining({ tipo_proceso_id: 20, predio: 'PUERTO BOSSETTI', hr_disposicion: 12 }),
      expect.objectContaining({ tipo_proceso_id: 21, predio: 'PUERTO BOSSETTI', hr_remolque: 5 }),
    ])
    expect(payload.operacion).toBeUndefined()
  })

  it('trims acta and rodal in the process payload', async () => {
    store.predios = [{ idPredio: 1, nombre: '  PUERTO BOSSETTI  ' }]
    const wrapper = mountView({ idUnidadNegocio: 7, nombre: '  Caminos  ' })
    const proceso = wrapper.vm.procesos[0]
    store.rodales = [{ idRodal: 2, rodal: '  R-1  ' }]
    wrapper.vm.rodalesPorProceso[proceso.key] = store.rodales

    wrapper.vm.form.fecha = '2026-08-14'
    wrapper.vm.form.cod_equipo = 10
    wrapper.vm.form.hr_inicio = 1
    wrapper.vm.form.hr_fin = 5
    proceso.tipo_proceso_id = 9
    proceso.predio_id = 1
    proceso.acta = '  ACTA-1  '
    proceso.rodal_id = 2
    proceso.km_perfilado = 3
    wrapper.vm.pasoActual = 8

    await wrapper.vm.guardar()

    const payload = store.submitParteCaminos.mock.calls[0][0]
    expect(payload.procesos[0]).toMatchObject({
      predio: 'PUERTO BOSSETTI',
      acta: 'ACTA-1',
      rodal: 'R-1',
    })
  })

  it('loads Caminos-scoped catalogs when mounted', async () => {
    mountView()

    await Promise.resolve()
    expect(store.fetchTiposProceso).toHaveBeenCalledWith(7)
    expect(store.fetchMoviles).toHaveBeenCalledWith(7)
    expect(store.fetchLugaresCarga).toHaveBeenCalledWith(7)
  })
})
