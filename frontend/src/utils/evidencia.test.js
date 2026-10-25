import { describe, expect, it } from 'vitest'
import {
  ESTADO_PENDIENTE,
  ESTADO_RECHAZADA,
  ESTADO_REEMPLAZADA,
  ESTADO_VERIFICADA,
  FILTROS_EVIDENCIA,
  esObservado,
  estadoLabel,
  estadoTone,
  rolLabel,
  tieneEvidenciaPendiente,
} from './evidencia'

describe('utilidades de la evidencia (issue #204)', () => {
  it('nombra cada rol segun lo que muestra la foto', () => {
    expect(rolLabel('procesador')).toBe('Foto de la pantalla del procesador')
    expect(rolLabel('horometro')).toBe('Foto del horómetro')
    expect(rolLabel('otro')).toBe('Foto de evidencia')
  })

  it('nombra cada estado de la foto', () => {
    expect(estadoLabel(ESTADO_PENDIENTE)).toBe('Pendiente de verificación')
    expect(estadoLabel(ESTADO_VERIFICADA)).toBe('Verificada')
    expect(estadoLabel(ESTADO_RECHAZADA)).toBe('Rechazada')
    expect(estadoLabel(ESTADO_REEMPLAZADA)).toBe('Reemplazada')
  })

  it('el tono del badge sigue al estado', () => {
    expect(estadoTone(ESTADO_VERIFICADA)).toBe('success')
    expect(estadoTone(ESTADO_RECHAZADA)).toBe('error')
    expect(estadoTone(ESTADO_REEMPLAZADA)).toBe('neutral')
    expect(estadoTone(ESTADO_PENDIENTE)).toBe('warning')
  })

  it('un registro con foto rechazada queda observado', () => {
    expect(esObservado({ evidencias_rechazadas: 1 })).toBe(true)
    expect(esObservado({ evidencias_rechazadas: 0 })).toBe(false)
    expect(esObservado({})).toBe(false)
    expect(esObservado(null)).toBe(false)
  })

  it('un registro con foto sin verificar tiene evidencia pendiente', () => {
    expect(tieneEvidenciaPendiente({ evidencias_pendientes: 2 })).toBe(true)
    expect(tieneEvidenciaPendiente({ evidencias_pendientes: 0 })).toBe(false)
    expect(tieneEvidenciaPendiente(null)).toBe(false)
  })

  it('el filtro ofrece todas las opciones del dashboard', () => {
    expect(FILTROS_EVIDENCIA.map((opcion) => opcion.value)).toEqual([
      '',
      'pendiente',
      'rechazada',
      'sin_evidencia',
    ])
  })
})
