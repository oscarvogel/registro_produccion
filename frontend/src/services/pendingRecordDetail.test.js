import { describe, expect, it } from 'vitest'
import { buildCaminosProcessGroups } from './pendingRecordDetail'

describe('buildCaminosProcessGroups', () => {
  it('muestra los procesos de Caminos guardados dentro de payload.procesos', () => {
    const groups = buildCaminosProcessGroups({
      procesos: [
        {
          tipo_proceso_id: 12,
          predio: 'SAN PEDRO',
          acta: '',
          rodal: '',
          km_perfilado: 7.5,
          hr_disposicion: 0,
          hr_remolque: 0,
        },
        {
          tipo_proceso_id: 18,
          predio: 'YERBAL',
          acta: 'ACTA-44',
          rodal: 'R-03',
          km_perfilado: 0,
          hr_disposicion: 0,
          hr_remolque: 2.25,
        },
      ],
    })

    expect(groups).toHaveLength(2)
    expect(groups[0].title).toBe('Proceso 1')
    expect(groups[0].fields).toEqual(expect.arrayContaining([
      expect.objectContaining({ label: 'Tipo de proceso ID', value: 12 }),
      expect.objectContaining({ label: 'Predio', value: 'SAN PEDRO' }),
      expect.objectContaining({ label: 'Kilómetros de perfilado', value: 7.5 }),
    ]))
    expect(groups[0].fields.some((field) => field.label === 'Horas de remolque')).toBe(false)

    expect(groups[1].fields).toEqual(expect.arrayContaining([
      expect.objectContaining({ label: 'Acta', value: 'ACTA-44' }),
      expect.objectContaining({ label: 'Rodal', value: 'R-03' }),
      expect.objectContaining({ label: 'Horas de remolque', value: 2.25 }),
    ]))
  })

  it('no agrega bloques cuando no hay procesos', () => {
    expect(buildCaminosProcessGroups({})).toEqual([])
    expect(buildCaminosProcessGroups({ procesos: [] })).toEqual([])
  })
})
