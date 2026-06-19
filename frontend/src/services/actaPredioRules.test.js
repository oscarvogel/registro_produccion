import { describe, expect, it } from 'vitest'

import {
  cleanLocationValues,
  getLocationRequirements,
  processRequiresActaPredio,
  shouldShowActaPredioFields,
} from './actaPredioRules'

describe('acta/predio rules', () => {
  it('uses backend flags as the primary source for granular requirements', () => {
    const requirements = getLocationRequirements({
      nombre: 'Fresa',
      requiere_acta: true,
      requiere_predio: false,
      requiere_rodal: true,
    })

    expect(requirements).toEqual({
      requiere_acta: true,
      requiere_predio: false,
      requiere_rodal: true,
    })
    expect(shouldShowActaPredioFields({ nombre: 'Fresa', requiere_acta: true })).toBe(true)
  })

  it('supports partial backend requirements independently', () => {
    expect(getLocationRequirements({ requiere_acta: true })).toEqual({
      requiere_acta: true,
      requiere_predio: false,
      requiere_rodal: false,
    })
    expect(getLocationRequirements({ requiere_predio: true, requiere_rodal: true })).toEqual({
      requiere_acta: false,
      requiere_predio: true,
      requiere_rodal: true,
    })
  })

  it.each([
    ['Arauco'],
    ['arauco'],
    ['Biomasa gajos'],
    ['BIOMASA - GAJOS'],
  ])('%s falls back to requiring Acta, Predio, and Rodal when backend flags are missing', (processName) => {
    expect(processRequiresActaPredio(processName)).toBe(true)
    expect(shouldShowActaPredioFields({ nombre: processName })).toBe(true)
    expect(getLocationRequirements({ nombre: processName })).toEqual({
      requiere_acta: true,
      requiere_predio: true,
      requiere_rodal: true,
    })
  })

  it.each([
    ['Fresa'],
    ['Papel'],
    ['Trabajos eventuales'],
    ['Biomasa general'],
    ['Transju'],
    ['Otros'],
  ])('%s falls back to not requiring location fields', (processName) => {
    expect(processRequiresActaPredio(processName)).toBe(false)
    expect(shouldShowActaPredioFields({ nombre: processName })).toBe(false)
  })

  it('cleans only location values that no longer apply', () => {
    const form = {
      acta: '123',
      predio_id: 77,
      rodal_id: 88,
      rodal_manual: 'A1',
    }

    cleanLocationValues(form, {
      requiere_acta: true,
      requiere_predio: false,
      requiere_rodal: false,
    })

    expect(form).toEqual({
      acta: '123',
      predio_id: '',
      rodal_id: '',
      rodal_manual: '',
    })
  })
})
