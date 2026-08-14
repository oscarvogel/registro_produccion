import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

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
  lugaresCarga: [],
  submitting: false,
  error: null,
  fetchTiposProceso: vi.fn(async () => []),
  fetchMoviles: vi.fn(async () => []),
  fetchLugaresCarga: vi.fn(async () => []),
  fetchPredios: vi.fn(async () => []),
  fetchActas: vi.fn(async () => []),
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

import CaminosFormView from './CaminosFormView.vue'


describe('CaminosFormView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('allows adding and removing process rows in the same daily part', async () => {
    const wrapper = mount(CaminosFormView, {
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

  it('loads Caminos-scoped catalogs when mounted', async () => {
    mount(CaminosFormView, {
      props: {
        unidad: { idUnidadNegocio: 7, nombre: 'Caminos' },
      },
      global: {
        stubs: {
          SectionCard: { template: '<section><slot /></section>' },
          InputField: { template: '<input />' },
        },
      },
    })

    await Promise.resolve()
    expect(store.fetchTiposProceso).toHaveBeenCalledWith(7)
    expect(store.fetchMoviles).toHaveBeenCalledWith(7)
    expect(store.fetchLugaresCarga).toHaveBeenCalledWith(7)
  })
})
