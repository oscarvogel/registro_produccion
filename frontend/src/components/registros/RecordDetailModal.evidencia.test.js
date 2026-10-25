import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

const auth = vi.hoisted(() => ({ user: { nombre: 'ENCARGADO UNO', encargado: 1 }, isAdmin: false }))
const toast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn(),
}))
const swal = vi.hoisted(() => ({ fire: vi.fn(async () => ({ value: 'el horometro no se ve' })) }))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))
vi.mock('@/stores/auth', () => ({
  useAuthStore: () => auth,
}))
vi.mock('@/stores/toast', () => ({
  useToastStore: () => toast,
}))
vi.mock('sweetalert2', () => ({
  default: { fire: swal.fire },
}))

import api from '@/services/api'
import RecordDetailModal from './RecordDetailModal.vue'

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
  AppBadge: { template: '<span><slot /></span>' },
  AppButton: {
    props: ['disabled', 'loading', 'variant', 'size'],
    template: '<button :disabled="disabled || loading" @click="$emit(\'click\')"><slot /></button>',
  },
}

const FOTO = {
  id: 77,
  registro_id: 42,
  form_uuid: 'uuid-42',
  tipo: 'procesador',
  incluye_horometro: 1,
  estado: 0,
  mime: 'image/jpeg',
  tamano: 1200,
}

function mockApi({ evidencias = [FOTO] } = {}) {
  api.get.mockImplementation((url) => {
    if (url === '/api/dashboard/registros/42') {
      return Promise.resolve({
        data: {
          id: 42,
          operacion: 'PROCESO',
          fecha: '2026-10-20',
          operador: 'OPERADOR UNO',
          evidencias_total: evidencias.length,
        },
      })
    }
    if (url === '/api/produccion/registros/42/evidencias') {
      return Promise.resolve({ data: evidencias })
    }
    if (url.includes('/archivo')) {
      return Promise.resolve({ data: new Blob(['foto']) })
    }
    return Promise.resolve({ data: {} })
  })
}

describe('seccion de evidencia del detalle del registro (issue #204)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
    auth.user = { nombre: 'ENCARGADO UNO', encargado: 1 }
    auth.isAdmin = false
    swal.fire.mockImplementation(async () => ({ value: 'el horometro no se ve' }))
    if (typeof URL.createObjectURL !== 'function') {
      URL.createObjectURL = vi.fn(() => 'blob:evidencia')
    }
    if (typeof URL.revokeObjectURL !== 'function') {
      URL.revokeObjectURL = vi.fn()
    }
  })

  it('muestra la foto, el rol y el aviso de la declaracion D7', async () => {
    mockApi()
    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    const seccion = wrapper.find('[data-testid="record-detail-evidencia"]')
    expect(seccion.exists()).toBe(true)
    expect(wrapper.text()).toContain('Evidencia fotográfica')
    expect(wrapper.text()).toContain('Foto de la pantalla del procesador')
    expect(wrapper.text()).toContain('Pendiente de verificación')
    // El aviso de D7 es el corazon del control: el operador declara que el
    // horometro se ve en la pantalla y el encargado lo contrasta.
    expect(wrapper.find('[data-testid="evidencia-declaracion"]').text()).toContain(
      'El operador declaró que el horómetro se ve en esta pantalla',
    )
    expect(wrapper.find('[data-testid="evidencia-foto"]').exists()).toBe(true)
  })

  it('el encargado puede verificar la foto', async () => {
    mockApi()
    api.patch.mockResolvedValue({ data: { ...FOTO, estado: 1, verificado_por: 'ENCARGADO UNO' } })

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    const boton = wrapper.find('[data-testid="verificar-77"]')
    expect(boton.exists()).toBe(true)
    await boton.trigger('click')
    await flushPromises()

    expect(api.patch).toHaveBeenCalledWith(
      '/api/produccion/evidencias/77',
      { estado: 1, comentario: '' },
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(wrapper.text()).toContain('Verificada')
    expect(toast.success).toHaveBeenCalled()
  })

  it('el rechazo pide el motivo y lo guarda', async () => {
    mockApi()
    api.patch.mockResolvedValue({
      data: { ...FOTO, estado: 2, comentario: 'el horometro no se ve', verificado_por: 'ENCARGADO UNO' },
    })

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    const boton = wrapper.find('[data-testid="rechazar-77"]')
    expect(boton.exists()).toBe(true)
    await boton.trigger('click')
    await flushPromises()

    expect(swal.fire).toHaveBeenCalled()
    expect(api.patch).toHaveBeenCalledWith(
      '/api/produccion/evidencias/77',
      { estado: 2, comentario: 'el horometro no se ve' },
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(wrapper.find('[data-testid="evidencia-motivo"]').text()).toContain(
      'el horometro no se ve',
    )
  })

  it('el operador NO ve los botones de verificar ni de rechazar', async () => {
    auth.user = { nombre: 'OPERADOR UNO', encargado: 0 }
    mockApi()

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    expect(wrapper.find('[data-testid="record-detail-evidencia"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="verificar-77"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="rechazar-77"]').exists()).toBe(false)
  })

  it('el admin tambien puede verificar', async () => {
    auth.isAdmin = true
    auth.user = { nombre: 'ADMIN UNO', encargado: 0 }
    mockApi()

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    expect(wrapper.find('[data-testid="verificar-77"]').exists()).toBe(true)
  })

  it('una foto sin la declaracion D7 no muestra el aviso', async () => {
    mockApi({ evidencias: [{ ...FOTO, tipo: 'horometro', incluye_horometro: 0 }] })

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    expect(wrapper.find('[data-testid="evidencia-declaracion"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('Foto del horómetro')
  })

  it('un registro sin evidencia no muestra la seccion', async () => {
    mockApi({ evidencias: [] })

    const wrapper = mount(RecordDetailModal, {
      props: { modelValue: true, registroId: 42 },
      global: { stubs: globalStubs },
    })
    await flushPromises()
    await flushPromises()

    expect(wrapper.find('[data-testid="record-detail-evidencia"]').exists()).toBe(false)
  })
})
