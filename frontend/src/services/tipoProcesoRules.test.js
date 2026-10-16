import { describe, expect, it } from 'vitest'

import { processRequiresHorometro, productionSteps } from './tipoProcesoRules'

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
