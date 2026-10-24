import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

vi.mock('@/services/db', () => ({
  default: {
    catalogos: {
      put: vi.fn(),
      get: vi.fn(async () => undefined),
    },
    pendingRecords: {
      count: vi.fn(async () => 0),
      delete: vi.fn(),
      update: vi.fn(),
      where: vi.fn(() => ({
        equals: vi.fn(() => ({
          count: vi.fn(async () => 0),
          toArray: vi.fn(async () => []),
        })),
      })),
    },
  },
}))

vi.mock('@/services/pendingRecords', () => ({
  ensurePendingIdentity: vi.fn(async (record) => record.payload),
  queuePendingProductionRecord: vi.fn(),
  pendingSubmissionEndpoint: vi.fn(() => '/api/produccion/'),
  stripPendingMetadata: vi.fn((payload) => payload),
  SUBMISSION_KIND_FIELD: '__submission_kind',
  SUBMISSION_KIND_CAMINOS: 'caminos',
}))

import api from '@/services/api'
import { useProduccionStore } from './produccion'

describe('subida de evidencia (issue #200)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('manda la foto como multipart con el form_uuid del formulario', async () => {
    api.post.mockResolvedValue({ data: { id: 42, tipo: 'procesador' } })
    const store = useProduccionStore()
    const archivo = new File([new Uint8Array(10)], 'foto.jpg', { type: 'image/jpeg' })

    const respuesta = await store.uploadEvidencia({
      formUuid: 'uuid-1',
      tipo: 'procesador',
      archivo,
      incluyeHorometro: true,
    })

    expect(respuesta.id).toBe(42)
    const [url, body, config] = api.post.mock.calls[0]
    expect(url).toBe('/api/produccion/evidencias')
    expect(body).toBeInstanceOf(FormData)
    expect(body.get('form_uuid')).toBe('uuid-1')
    expect(body.get('tipo')).toBe('procesador')
    expect(body.get('incluye_horometro')).toBe('true')
    // multipart: con el Content-Type por defecto (json) axios manda el
    // FormData como JSON y el backend no lo entiende.
    expect(config.headers['Content-Type']).toBe('multipart/form-data')
  })

  it('manda la declaracion en false cuando el operador no declara el horometro', async () => {
    api.post.mockResolvedValue({ data: { id: 43, tipo: 'horometro' } })
    const store = useProduccionStore()
    const archivo = new File([new Uint8Array(10)], 'foto.jpg', { type: 'image/jpeg' })

    await store.uploadEvidencia({ formUuid: 'uuid-2', tipo: 'horometro', archivo })

    const body = api.post.mock.calls[0][1]
    expect(body.get('incluye_horometro')).toBe('false')
  })

  it('propaga el error si la subida falla', async () => {
    api.post.mockRejectedValue(new Error('sin conexion'))
    const store = useProduccionStore()
    const archivo = new File([new Uint8Array(10)], 'foto.jpg', { type: 'image/jpeg' })

    await expect(
      store.uploadEvidencia({ formUuid: 'uuid-3', tipo: 'procesador', archivo })
    ).rejects.toThrow('sin conexion')
  })
})
