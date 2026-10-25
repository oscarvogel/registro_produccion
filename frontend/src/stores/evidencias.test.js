import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}))

import api from '@/services/api'
import { useEvidenciasStore } from './evidencias'

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

describe('store de evidencias (issue #204)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
    if (typeof URL.createObjectURL !== 'function') {
      URL.createObjectURL = vi.fn(() => 'blob:evidencia')
    }
    if (typeof URL.revokeObjectURL !== 'function') {
      URL.revokeObjectURL = vi.fn()
    }
  })

  it('carga la evidencia del registro y baja las fotos', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/produccion/registros/42/evidencias') {
        return Promise.resolve({ data: [FOTO] })
      }
      if (url === '/api/produccion/evidencias/77/archivo') {
        return Promise.resolve({ data: new Blob(['foto']) })
      }
      return Promise.resolve({ data: {} })
    })

    const store = useEvidenciasStore()
    await store.cargar(42)

    expect(store.evidencias).toHaveLength(1)
    expect(store.evidencias[0].id).toBe(77)
    expect(store.urls[77]).toBe('blob:evidencia')
    expect(store.tieneEvidencias).toBe(true)
    expect(store.pendientes).toHaveLength(1)
  })

  it('no pide la lista si el registro no tiene evidencia', async () => {
    const store = useEvidenciasStore()
    await store.cargar(null)

    expect(api.get).not.toHaveBeenCalled()
    expect(store.evidencias).toHaveLength(0)
  })

  it('deja un mensaje de error si la lista no se puede cargar', async () => {
    api.get.mockRejectedValue(new Error('boom'))
    const store = useEvidenciasStore()

    await store.cargar(42)

    expect(store.error).toBe('No se pudieron cargar las fotos de evidencia')
    expect(store.evidencias).toHaveLength(0)
  })

  it('verificar una foto la actualiza en la lista', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/produccion/registros/42/evidencias') {
        return Promise.resolve({ data: [FOTO] })
      }
      return Promise.resolve({ data: new Blob(['foto']) })
    })
    api.patch.mockResolvedValue({ data: { ...FOTO, estado: 1, verificado_por: 'ENCARGADO' } })

    const store = useEvidenciasStore()
    await store.cargar(42)
    await store.verificar(77, { estado: 1 })

    expect(api.patch).toHaveBeenCalledWith(
      '/api/produccion/evidencias/77',
      { estado: 1, comentario: '' },
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.evidencias[0].estado).toBe(1)
    expect(store.pendientes).toHaveLength(0)
  })

  it('rechazar guarda el motivo y deja la foto rechazada', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/produccion/registros/42/evidencias') {
        return Promise.resolve({ data: [FOTO] })
      }
      return Promise.resolve({ data: new Blob(['foto']) })
    })
    api.patch.mockResolvedValue({
      data: { ...FOTO, estado: 2, comentario: 'el horómetro no se ve' },
    })

    const store = useEvidenciasStore()
    await store.cargar(42)
    await store.verificar(77, { estado: 2, comentario: 'el horómetro no se ve' })

    expect(api.patch.mock.calls[0][1]).toEqual({
      estado: 2,
      comentario: 'el horómetro no se ve',
    })
    expect(store.rechazadas).toHaveLength(1)
  })

  it('limpiar libera las object URLs y vacia la lista', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/produccion/registros/42/evidencias') {
        return Promise.resolve({ data: [FOTO] })
      }
      return Promise.resolve({ data: new Blob(['foto']) })
    })

    const store = useEvidenciasStore()
    await store.cargar(42)
    store.limpiar()

    expect(store.evidencias).toHaveLength(0)
    expect(store.urls).toEqual({})
    expect(store.registroId).toBeNull()
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:evidencia')
  })
})
