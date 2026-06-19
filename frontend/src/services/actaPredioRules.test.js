import { describe, expect, it } from 'vitest'

import {
  cleanActaPredioValues,
  processRequiresActaPredio,
  shouldShowActaPredioFields,
} from './actaPredioRules'

describe('acta/predio rules', () => {
  it.each([
    ['Arauco'],
    ['arauco'],
    ['Biomasa gajos'],
    ['BIOMASA - GAJOS'],
  ])('%s requires Acta and Predio', (processName) => {
    expect(processRequiresActaPredio(processName)).toBe(true)
    expect(shouldShowActaPredioFields({ nombre: processName })).toBe(true)
  })

  it.each([
    ['Fresa'],
    ['Papel'],
    ['Trabajos eventuales'],
    ['Biomasa general'],
    ['Transju'],
    ['Otros'],
  ])('%s does not require Acta or Predio', (processName) => {
    expect(processRequiresActaPredio(processName)).toBe(false)
    expect(shouldShowActaPredioFields({ nombre: processName })).toBe(false)
  })

  it('cleans Acta and Predio location values when switching to a process that does not require them', () => {
    const form = {
      acta: '123',
      predio_id: 77,
      rodal_id: 88,
      rodal_manual: 'A1',
    }

    cleanActaPredioValues(form)

    expect(form).toEqual({
      acta: '',
      predio_id: '',
      rodal_id: '',
      rodal_manual: '',
    })
  })
})
