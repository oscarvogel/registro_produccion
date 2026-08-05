import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import RecordDetailModal from './RecordDetailModal.vue'
import { useDashboardRegistrosStore } from '@/stores/dashboardRegistros'

// Stub del wrapper de modal: no necesitamos Teleport ni animaciones en el test,
// solo queremos asegurar que el slot/payload se renderice segun el estado del store.
const AppModalStub = {
  name: 'AppModal',
  props: ['modelValue', 'title', 'description'],
  emits: ['update:modelValue'],
  template: `
    <div v-if="modelValue" data-testid="app-modal">
      <h3>{{ title }}</h3>
      <p v-if="description">{{ description }}</p>
      <slot />
      <slot name="actions" />
    </div>
  `,
}

const globalStubs = {
  AppModal: AppModalStub,
  AppIcon: { template: '<span />' },
}

describe('RecordDetailModal (issue #123)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('al abrir con un registroId dispara fetchDetalle y muestra el resumen del registro', async () => {
    api.get.mockResolvedValueOnce({
      data: {
        id: 42,
        fecha: '2026-08-04',
        operacion: 'Cosecha',
        operador: 'Juan Perez',
        equipo: 'Maquina 1',
        hr_inicio: 8,
        hr_fin: 12,
        combustible: 50,
      },
    })
    const store = useDashboardRegistrosStore()
    const fetchSpy = vi.spyOn(store, 'fetchDetalle')

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })

    expect(fetchSpy).toHaveBeenCalledWith(42)
    await flushPromises()
    await flushPromises()

    expect(api.get).toHaveBeenCalledWith(
      '/api/dashboard/registros/42',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(wrapper.find('[data-testid="record-detail-content"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Cosecha')
    expect(wrapper.text()).toContain('04/08/2026')
  })

  it('muestra el bloque de loading mientras fetchDetalle esta en curso', async () => {
    let resolveFetch
    api.get.mockImplementationOnce(
      () => new Promise((resolve) => { resolveFetch = resolve }),
    )

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 7 },
      global: { stubs: globalStubs },
    })
    // El watch (immediate:true) dispara el fetch en mount.
    await flushPromises()

    expect(wrapper.find('[data-testid="record-detail-loading"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="record-detail-content"]').exists()).toBe(false)

    resolveFetch({ data: { id: 7, operacion: 'Cosecha', fecha: '2026-08-04' } })
    await flushPromises()
    await flushPromises()

    expect(wrapper.find('[data-testid="record-detail-loading"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="record-detail-content"]').exists()).toBe(true)
  })

  it('muestra el mensaje de error cuando fetchDetalle falla con 404', async () => {
    const err = new Error('Not found')
    err.response = { status: 404 }
    api.get.mockRejectedValueOnce(err)

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 999 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    expect(wrapper.find('[data-testid="record-detail-error"]').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/fuera de tu alcance/i)
  })

  it('al cerrar (modelValue=false) llama a clearDetalle para no mostrar datos stale', async () => {
    api.get.mockResolvedValueOnce({ data: { id: 1, operacion: 'Cosecha' } })
    const store = useDashboardRegistrosStore()
    const clearSpy = vi.spyOn(store, 'clearDetalle')
    store.fetchDetalle(1)
    await flushPromises()

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 1 },
      global: { stubs: globalStubs },
    })
    await flushPromises()

    await wrapper.setProps({ modelValue: false })
    expect(clearSpy).toHaveBeenCalled()
  })

  it('al cambiar de registroId reabre el fetch del nuevo id', async () => {
    api.get.mockResolvedValueOnce({ data: { id: 1, operacion: 'A' } })
    api.get.mockResolvedValueOnce({ data: { id: 2, operacion: 'B' } })
    const store = useDashboardRegistrosStore()
    const fetchSpy = vi.spyOn(store, 'fetchDetalle')

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 1 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    expect(fetchSpy).toHaveBeenCalledWith(1)

    await wrapper.setProps({ registroId: 2 })
    await flushPromises()

    expect(fetchSpy).toHaveBeenCalledWith(2)
    expect(fetchSpy).toHaveBeenCalledTimes(2)
    expect(store.detalle).toEqual({ id: 2, operacion: 'B' })
  })

  it('no dispara fetch si el modal abre sin registroId', async () => {
    const store = useDashboardRegistrosStore()
    const fetchSpy = vi.spyOn(store, 'fetchDetalle')

    mount(RecordDetailModal, {
      props: { modelValue: true, registroId: null },
      global: { stubs: globalStubs },
    })
    await flushPromises()

    expect(fetchSpy).not.toHaveBeenCalled()
    expect(api.get).not.toHaveBeenCalled()
  })
})

describe('RecordDetailModal (issue #129) oculta campos vacios', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  /** Helper: monta el modal, deja resolver el fetch y devuelve el wrapper. */
  async function mountConDetalle(detalle) {
    api.get.mockResolvedValueOnce({ data: detalle })
    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: detalle.id },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()
    return wrapper
  }

  it('omite campos con null/0/empty string del DOM', async () => {
    const wrapper = await mountConDetalle({
      id: 1,
      operacion: 'Cosecha',
      fecha: '2026-08-04',
      // todos los demas campos null/0
      hr_inicio: 0,
      hr_fin: 0,
      hrs_no_op: 0,
      motivo_no_op: '',
      produccion: 0,
      combustible: 0,
    })

    expect(wrapper.find('[data-testid="record-detail-content"]').exists()).toBe(true)
    // Titulo sigue mostrando operacion + fecha
    expect(wrapper.text()).toContain('Cosecha')
    expect(wrapper.text()).toContain('04/08/2026')
    // Labels que NO deben aparecer (porque sus valores son 0/null/empty)
    expect(wrapper.text()).not.toContain('Hora inicio')
    expect(wrapper.text()).not.toContain('Hora fin')
    expect(wrapper.text()).not.toContain('Horas no operativas')
    expect(wrapper.text()).not.toContain('Motivo no operativo')
    expect(wrapper.text()).not.toContain('Produccion')
    expect(wrapper.text()).not.toContain('Combustible')
  })

  it('omite grupos enteros cuando todos sus campos son vacios', async () => {
    const wrapper = await mountConDetalle({
      id: 2,
      operacion: 'Cosecha',
      fecha: '2026-08-04',
      // grupo Identificacion tiene al menos operacion + fecha con dato
      // grupo Produccion queda 100% vacio
      produccion: 0,
      unitario: 0,
      tn_despachadas: 0,
      m3: 0,
      has: 0,
      // grupo Consumos queda 100% vacio
      combustible: 0,
      aceite_cadena: 0,
      aceite_hidraulico: 0,
      aceite_motor: 0,
      aceite_embrague: 0,
      aceite_transmision: 0,
    })

    // Header "Identificacion" aparece (tiene operacion + fecha)
    expect(wrapper.text()).toContain('Identificacion')
    // Headers de grupos vacios NO aparecen
    expect(wrapper.text()).not.toContain('Produccion')
    expect(wrapper.text()).not.toContain('Consumos')
  })

  it('sigue mostrando el ID del registro en el footer aunque el contenido este vacio', async () => {
    const wrapper = await mountConDetalle({
      id: 999,
      operacion: 'X',
      fecha: '2026-08-04',
    })

    // Aunque hipoteticamente todos los grupos quedaran vacios, el ID del
    // footer siempre se ve.
    expect(wrapper.text()).toContain('ID #999')
  })

  it('muestra un grupo que tiene al menos un campo con dato aunque otros esten vacios', async () => {
    const wrapper = await mountConDetalle({
      id: 3,
      operacion: 'Cosecha',
      fecha: '2026-08-04',
      produccion: 0,
      tn_despachadas: 150,  // unico campo con dato en grupo Produccion
      m3: 0,
    })

    expect(wrapper.text()).toContain('Produccion')
    expect(wrapper.text()).toContain('Toneladas')
    expect(wrapper.text()).toContain('150')
    // El resto del grupo Produccion esta vacio
    expect(wrapper.text()).not.toContain('Hectareas')
    expect(wrapper.text()).not.toContain('KM carreteo')
  })
})
