import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
  },
}))

import api from '@/services/api'
import { useMisRegistrosStore } from './misRegistros'

describe('misRegistros store - toast suppression on local fallback', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('fetchMisRegistros passes _suppressErrorToast when falling back to empty registros', async () => {
    api.get.mockRejectedValueOnce(new Error('boom'))
    const store = useMisRegistrosStore()
    store.initFiltros()

    await store.fetchMisRegistros()

    expect(api.get).toHaveBeenCalledWith(
      '/api/produccion/mis-registros',
      expect.objectContaining({ _suppressErrorToast: true }),
    )
    expect(store.registros).toEqual([])
    expect(store.error).toBe('No se pudieron cargar los registros')
  })

  it('uses the equipment stock summary for the fuel card', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/produccion/mis-registros') {
        return Promise.resolve({
          data: {
            registros: [
              {
                id: 100,
                fecha: '2026-11-03',
                operacion: 'CARGA',
                equipo: 'GRUA N11',
                cod_equipo: 10,
                combustible: 90,
                hr_inicio: 4660,
                hr_fin: 4665,
              },
            ],
          },
        })
      }
      if (url === '/api/produccion/caminos/mis-registros') {
        return Promise.resolve({ data: { registros: [], child_ids: [] } })
      }
      if (url === '/api/combustible/resumen-equipos') {
        return Promise.resolve({
          data: {
            total_egresos: 415,
            total_horas: 26,
            por_equipo: [
              {
                id_movil: 10,
                nombre: 'GRUA N11',
                total_egresos: 415,
                total_horas: 26,
                consumo_por_hora: 15.96,
              },
            ],
          },
        })
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`))
    })
    const store = useMisRegistrosStore()
    store.initFiltros()

    await store.fetchMisRegistros()

    expect(api.get).toHaveBeenCalledWith(
      '/api/combustible/resumen-equipos',
      expect.objectContaining({
        params: expect.objectContaining({ equipos: '10' }),
        _suppressErrorToast: true,
      }),
    )
    expect(store.totales.total_combustible).toBe(415)
    expect(store.totales.total_horas_equipo).toBe(26)
    expect(store.totales.combustible_por_hora).toBe(15.96)
    expect(store.totales.por_equipo).toHaveLength(1)
    expect(store.totales.por_equipo[0]).toMatchObject({
      id_movil: 10,
      nombre: 'GRUA N11',
      total_egresos: 415,
      consumo_por_hora: 15.96,
    })
    // El detalle del parte sí muestra los litros del libro vinculado.
    expect(store.registros[0].combustible).toBe(90)
  })

  it('no usa los litros declarados del parte si falta el resumen del equipo', async () => {
    api.get.mockImplementation((url) => {
      if (url === '/api/produccion/mis-registros') {
        return Promise.resolve({
          data: {
            registros: [
              {
                id: 100,
                fecha: '2026-11-03',
                operacion: 'CARGA',
                equipo: 'GRUA N11',
                cod_equipo: 10,
                combustible: 90,
                hr_inicio: 4660,
                hr_fin: 4665,
              },
            ],
          },
        })
      }
      if (url === '/api/produccion/caminos/mis-registros') {
        return Promise.resolve({ data: { registros: [], child_ids: [] } })
      }
      if (url === '/api/combustible/resumen-equipos') {
        return Promise.reject(new Error('sin resumen'))
      }
      return Promise.reject(new Error(`Unexpected URL: ${url}`))
    })
    const store = useMisRegistrosStore()
    store.initFiltros()

    await store.fetchMisRegistros()

    expect(store.totales.total_combustible).toBe(0)
    expect(store.totales.total_horas_equipo).toBe(0)
    expect(store.totales.combustible_por_hora).toBeNull()
    // El detalle del parte sigue mostrando lo que devuelve la API.
    expect(store.registros[0].combustible).toBe(90)
  })
})