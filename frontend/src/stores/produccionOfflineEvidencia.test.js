import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const registros = []
const evidencias = []
let secuenciaRegistro = 0
let secuenciaEvidencia = 0
const llamadas = []
// Error que se va a injectar en la proxima subida de evidencia.
let falloEvidencia = null

function coleccion(filas, secuencia) {
  return {
    async add(row) {
      const id = (filas === registros ? ++secuenciaRegistro : ++secuenciaEvidencia)
      filas.push({ id, ...row })
      return id
    },
    async update(id, patch) {
      const fila = filas.find((item) => item.id === id)
      if (fila) Object.assign(fila, patch)
      return 1
    },
    async delete(id) {
      const index = filas.findIndex((item) => item.id === id)
      if (index >= 0) filas.splice(index, 1)
    },
    where(campo) {
      return {
        equals(valor) {
          return {
            async toArray() {
              return filas.filter((fila) => fila[campo] === valor)
            },
            async count() {
              return filas.filter((fila) => fila[campo] === valor).length
            },
            async delete() {
              const quedan = filas.filter((fila) => fila[campo] !== valor)
              const borradas = filas.length - quedan.length
              filas.length = 0
              filas.push(...quedan)
              return borradas
            },
          }
        },
      }
    },
    async toArray() {
      return [...filas]
    },
    async count() {
      return filas.length
    },
  }
}

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(async (url, body) => {
      // La llamada se registra SIEMPRE, incluso cuando falla: el orden de
      // los intentos es justamente lo que hay que verificar.
      llamadas.push({ url, body })
      if (url === '/api/produccion/evidencias') {
        if (falloEvidencia) {
          const error = falloEvidencia
          falloEvidencia = null
          throw error
        }
        return { data: { id: 77, tipo: body.get?.('tipo') } }
      }
      return { data: { id: 900 } }
    }),
  },
}))

vi.mock('@/services/db', () => ({
  default: {
    pendingRecords: {
      add: (row) => coleccion(registros).add(row),
      update: (id, patch) => coleccion(registros).update(id, patch),
      delete: (id) => coleccion(registros).delete(id),
      where: (campo) => coleccion(registros).where(campo),
      toArray: () => coleccion(registros).toArray(),
      count: async () => registros.length,
    },
    pendingEvidencias: {
      add: (row) => coleccion(evidencias).add(row),
      update: (id, patch) => coleccion(evidencias).update(id, patch),
      delete: (id) => coleccion(evidencias).delete(id),
      where: (campo) => coleccion(evidencias).where(campo),
      toArray: () => coleccion(evidencias).toArray(),
      count: async () => evidencias.length,
    },
    catalogos: {
      put: vi.fn(),
      get: vi.fn(async () => undefined),
    },
  },
}))

import db from '@/services/db'
import { useProduccionStore } from './produccion'

describe('modo offline de la evidencia (issue #202)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    registros.length = 0
    evidencias.length = 0
    secuenciaRegistro = 0
    secuenciaEvidencia = 0
    llamadas.length = 0
    falloEvidencia = null
    vi.clearAllMocks()
  })

  it('encola la foto del formulario', async () => {
    const store = useProduccionStore()
    const blob = new Blob(['foto'], { type: 'image/jpeg' })

    await store.encolarEvidencias({
      formUuid: 'uuid-1',
      fotos: [{ tipo: 'procesador', blob, incluyeHorometro: true, nombre: 'foto.jpg' }],
    })

    expect(evidencias).toHaveLength(1)
    expect(evidencias[0]).toMatchObject({
      formUuid: 'uuid-1',
      tipo: 'procesador',
      incluyeHorometro: 1,
      synced: 0,
    })
    expect(store.pendingEvidenceCount).toBe(1)
  })

  it('sube PRIMERO la evidencia y DESPUES el parte, con los ids en el payload', async () => {
    const store = useProduccionStore()
    await store.encolarEvidencias({
      formUuid: 'uuid-1',
      fotos: [{ tipo: 'procesador', blob: new Blob(['foto']), incluyeHorometro: true }],
    })
    await db.pendingRecords.add({
      payload: { form_uuid: 'uuid-1', UN: 'Demo', fecha: '2026-10-24' },
      clientId: 'uuid-1',
      timestamp: Date.now(),
      synced: 0,
      syncStatus: 'pending',
      retryCount: 0,
    })

    const resultado = await store.syncPending()

    expect(resultado.successCount).toBe(1)
    // El orden es la regla clave: primero la foto, despues el parte.
    expect(llamadas.map((llamada) => llamada.url)).toEqual([
      '/api/produccion/evidencias',
      '/api/produccion/',
    ])
    const payload = llamadas[1].body
    expect(payload.evidencias).toEqual([77])
    expect(payload.form_uuid).toBe('uuid-1')
    // La foto queda marcada como subida y el parte desaparece de la cola.
    expect(evidencias[0].synced).toBe(1)
    expect(registros).toHaveLength(0)
  })

  it('NO envia el parte si la foto no se pudo subir', async () => {
    const store = useProduccionStore()
    await store.encolarEvidencias({
      formUuid: 'uuid-1',
      fotos: [{ tipo: 'procesador', blob: new Blob(['foto']) }],
    })
    await db.pendingRecords.add({
      payload: { form_uuid: 'uuid-1' },
      clientId: 'uuid-1',
      timestamp: Date.now(),
      synced: 0,
      syncStatus: 'pending',
      retryCount: 0,
    })
    falloEvidencia = new Error('sin conexion')

    const resultado = await store.syncPending()

    expect(resultado.successCount).toBe(0)
    // Solo se intentó la foto: el parte no salió.
    expect(llamadas.map((llamada) => llamada.url)).toEqual(['/api/produccion/evidencias'])
    expect(registros).toHaveLength(1)
    expect(registros[0].syncStatus).toBe('pending')
    expect(evidencias[0].synced).toBe(0)
  })

  it('deja el payload intacto si no hay foto encolada', async () => {
    const store = useProduccionStore()
    await db.pendingRecords.add({
      payload: { form_uuid: 'uuid-2', UN: 'Demo' },
      clientId: 'uuid-2',
      timestamp: Date.now(),
      synced: 0,
      syncStatus: 'pending',
      retryCount: 0,
    })

    const resultado = await store.syncPending()

    expect(resultado.successCount).toBe(1)
    expect(llamadas).toHaveLength(1)
    expect(llamadas[0].url).toBe('/api/produccion/')
    expect(llamadas[0].body.evidencias).toBeUndefined()
  })
})
