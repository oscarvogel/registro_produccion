import { describe, expect, it } from 'vitest'

import {
  processRequiresHorometro,
  productionSteps,
  processRequiresEvidence,
  evidenceRoles,
  ROL_HOROMETRO,
  ROL_PROCESADOR,
} from './tipoProcesoRules'

describe('processRequiresHorometro', () => {
  it('respeta el flag del backend cuando es false', () => {
    expect(processRequiresHorometro({ nombre: 'Camioneta', requiere_horometro: false })).toBe(false)
  })

  it('respeta el flag del backend cuando es true', () => {
    expect(processRequiresHorometro({ nombre: 'HORAS MAQUINAS', requiere_horometro: true })).toBe(true)
  })

  it('asume true cuando el tipo de proceso no trae el flag', () => {
    expect(processRequiresHorometro({ nombre: 'Proceso viejo' })).toBe(true)
  })

  it('asume true cuando no hay tipo de proceso seleccionado', () => {
    expect(processRequiresHorometro(null)).toBe(true)
    expect(processRequiresHorometro(undefined)).toBe(true)
  })
})

describe('productionSteps', () => {
  it('incluye el paso Tiempo cuando el proceso requiere horometro', () => {
    const steps = productionSteps({ requiere_horometro: true })

    expect(steps.map((s) => s.key)).toContain('tiempo')
    expect(steps).toHaveLength(9)
  })

  it('omite el paso Tiempo cuando el proceso no requiere horometro', () => {
    const steps = productionSteps({ nombre: 'Camioneta', requiere_horometro: false })

    expect(steps.map((s) => s.key)).not.toContain('tiempo')
    expect(steps.map((s) => s.key)).toEqual([
      'contexto',
      'operador',
      'equipo',
      'proceso',
      'produccion',
      'consumos',
      'ubicacion',
      'revision',
    ])
  })

  it('conserva el resto de los pasos cuando no hay tipo de proceso', () => {
    expect(productionSteps(null)).toHaveLength(9)
  })
})

describe('evidencia fotografica (issue #200)', () => {
  it('incluye el paso Evidencia cuando el proceso exige foto', () => {
    const steps = productionSteps({
      requiere_horometro: true,
      requiere_foto_horometro: true,
      requiere_foto_procesador: true,
    })

    expect(steps.map((s) => s.key)).toContain('evidencia')
  })

  it('omite el paso Evidencia cuando el proceso no exige foto', () => {
    const steps = productionSteps({
      requiere_horometro: true,
      requiere_foto_horometro: false,
      requiere_foto_procesador: false,
    })

    expect(steps.map((s) => s.key)).not.toContain('evidencia')
  })

  it('omite el paso Evidencia cuando no hay tipo de proceso', () => {
    expect(processRequiresEvidence(null)).toBe(false)
    expect(productionSteps(null).map((s) => s.key)).not.toContain('evidencia')
  })

  it('coloca el paso Evidencia entre Produccion y Consumos', () => {
    const claves = productionSteps({
      requiere_horometro: true,
      requiere_foto_horometro: true,
      requiere_foto_procesador: true,
    }).map((s) => s.key)

    expect(claves.indexOf('evidencia')).toBe(claves.indexOf('produccion') + 1)
    expect(claves.indexOf('evidencia')).toBe(claves.indexOf('consumos') - 1)
  })

  it('devuelve los roles que exige el tipo de proceso', () => {
    expect(evidenceRoles({ requiere_foto_procesador: true, requiere_foto_horometro: true }))
      .toEqual([ROL_PROCESADOR, ROL_HOROMETRO])
    expect(evidenceRoles({ requiere_foto_procesador: true })).toEqual([ROL_PROCESADOR])
    expect(evidenceRoles({ requiere_foto_horometro: true })).toEqual([ROL_HOROMETRO])
    expect(evidenceRoles({})).toEqual([])
    expect(evidenceRoles(null)).toEqual([])
  })

  it('detecta que el proceso exige evidencia con cualquiera de los dos flags', () => {
    expect(processRequiresEvidence({ requiere_foto_procesador: true })).toBe(true)
    expect(processRequiresEvidence({ requiere_foto_horometro: true })).toBe(true)
    expect(processRequiresEvidence({ requiere_foto_procesador: false })).toBe(false)
  })
})
