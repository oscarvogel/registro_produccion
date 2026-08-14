import { describe, expect, it } from 'vitest'

import { groupCaminosRows } from './dashboardRegistros'
import { calculateGroupedTotals } from './misRegistros'


describe('Caminos grouping', () => {
  const siblings = [
    {
      id: 1,
      form_uuid: 'parte-1',
      fecha: '2026-08-14',
      operacion: 'PERFILADO',
      equipo: 'Motoniveladora',
      hr_inicio: 1200,
      hr_fin: 1210,
      combustible: 100,
      km_perfilado: 8.5,
      hr_disposicion: 0,
      hr_remolque: 0,
    },
    {
      id: 2,
      form_uuid: 'parte-1',
      fecha: '2026-08-14',
      operacion: 'DISPOSICION',
      equipo: 'Motoniveladora',
      hr_inicio: 1200,
      hr_fin: 1210,
      combustible: 100,
      km_perfilado: 0,
      hr_disposicion: 2,
      hr_remolque: 0,
    },
    {
      id: 3,
      form_uuid: 'parte-1',
      fecha: '2026-08-14',
      operacion: 'REMOLQUE',
      equipo: 'Motoniveladora',
      hr_inicio: 1200,
      hr_fin: 1210,
      combustible: 100,
      km_perfilado: 0,
      hr_disposicion: 0,
      hr_remolque: 1.5,
    },
  ]

  it('collapses sibling rows and keeps replicated header values once', () => {
    const grouped = groupCaminosRows(siblings)

    expect(grouped).toHaveLength(1)
    expect(grouped[0]).toMatchObject({
      id: 1,
      operacion: 'Caminos — 3 procesos',
      procesos_count: 3,
      combustible: 100,
      km_perfilado: 8.5,
      hr_disposicion: 2,
      hr_remolque: 1.5,
    })
  })

  it('calculates operator totals from the grouped part, not each child row', () => {
    const grouped = groupCaminosRows(siblings)
    const totals = calculateGroupedTotals(grouped)

    expect(totals.total).toBe(1)
    expect(totals.total_horas).toBe(10)
    expect(totals.total_combustible).toBe(100)
    expect(totals.total_km_perfilado).toBe(8.5)
    expect(totals.total_hr_disposicion).toBe(2)
    expect(totals.total_hr_remolque).toBe(1.5)
  })
})
