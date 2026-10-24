import { beforeEach, describe, expect, it, vi } from 'vitest'

const filas = []
let secuencia = 0

vi.mock('@/services/db', () => ({
  default: {
    pendingEvidencias: {
      async add(row) {
        secuencia += 1
        filas.push({ id: secuencia, ...row })
        return secuencia
      },
      async update(id, patch) {
        const fila = filas.find((item) => item.id === id)
        if (fila) Object.assign(fila, patch)
        return 1
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
    },
  },
}))

import {
  contarEvidenciasPendientes,
  eliminarEvidenciasDeFormulario,
  listarEvidenciasPendientes,
  marcarEvidenciaSincronizada,
  queuePendingEvidencia,
} from './pendingEvidencias'

describe('cola offline de evidencias (issue #202)', () => {
  beforeEach(() => {
    filas.length = 0
    secuencia = 0
    vi.clearAllMocks()
  })

  it('guarda el Blob crudo con el form_uuid y el tipo', async () => {
    const blob = new Blob(['foto'], { type: 'image/jpeg' })

    const id = await queuePendingEvidencia({
      formUuid: 'uuid-1',
      tipo: 'procesador',
      blob,
      incluyeHorometro: true,
      nombre: 'foto.jpg',
    })

    expect(id).toBe(1)
    expect(filas[0]).toMatchObject({
      formUuid: 'uuid-1',
      tipo: 'procesador',
      incluyeHorometro: 1,
      nombre: 'foto.jpg',
      synced: 0,
      syncStatus: 'pending',
    })
    // El Blob va crudo: no se pasa a base64.
    expect(filas[0].blob).toBe(blob)
  })

  it('devuelve solo las fotos de ese formulario, en orden', async () => {
    await queuePendingEvidencia({ formUuid: 'uuid-1', tipo: 'procesador', blob: new Blob(['a']) })
    await queuePendingEvidencia({ formUuid: 'uuid-2', tipo: 'procesador', blob: new Blob(['b']) })
    await queuePendingEvidencia({ formUuid: 'uuid-1', tipo: 'horometro', blob: new Blob(['c']) })

    const pendientes = await listarEvidenciasPendientes('uuid-1')

    expect(pendientes).toHaveLength(2)
    expect(pendientes.map((fila) => fila.tipo)).toEqual(['procesador', 'horometro'])
  })

  it('cuenta las fotos que todavia no se subieron', async () => {
    await queuePendingEvidencia({ formUuid: 'uuid-1', tipo: 'procesador', blob: new Blob(['a']) })
    const id = await queuePendingEvidencia({ formUuid: 'uuid-1', tipo: 'horometro', blob: new Blob(['b']) })

    expect(await contarEvidenciasPendientes()).toBe(2)

    await marcarEvidenciaSincronizada(id)

    expect(await contarEvidenciasPendientes()).toBe(1)
  })

  it('borra las fotos de un formulario', async () => {
    await queuePendingEvidencia({ formUuid: 'uuid-1', tipo: 'procesador', blob: new Blob(['a']) })
    await queuePendingEvidencia({ formUuid: 'uuid-2', tipo: 'procesador', blob: new Blob(['b']) })

    await eliminarEvidenciasDeFormulario('uuid-1')

    expect(filas).toHaveLength(1)
    expect(filas[0].formUuid).toBe('uuid-2')
  })
})
