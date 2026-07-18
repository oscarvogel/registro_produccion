import { describe, expect, it } from 'vitest'

import { createNavigationAreas, flattenNavigationItems } from './navigation'

function routeNames(areas) {
  return flattenNavigationItems(areas).map((item) => item.to.name)
}

describe('role-aware navigation', () => {
  it('keeps the operator navigation compact and without duplicate routes', () => {
    const areas = createNavigationAreas({ pendingCount: 3 })

    expect(areas.map((area) => area.key)).toEqual(['home', 'produccion', 'combustible'])
    expect(routeNames(areas)).toEqual(['home', 'produccion', 'pendientes', 'mis-registros', 'combustible'])
    expect(new Set(routeNames(areas)).size).toBe(routeNames(areas).length)
    expect(areas.find((area) => area.key === 'produccion').items[1].badge).toBe(3)
  })

  it('shows the operational dashboard but not personal records to an encargado', () => {
    const areas = createNavigationAreas({ isEncargado: true })

    expect(areas.map((area) => area.key)).toEqual(['home', 'produccion', 'combustible', 'dashboard'])
    expect(routeNames(areas)).toEqual(['home', 'produccion', 'pendientes', 'combustible', 'dashboard'])
  })

  it('keeps the administrator at five top-level areas and routes management through the center', () => {
    const areas = createNavigationAreas({ isAdmin: true, isEncargado: true })
    const names = routeNames(areas)

    expect(areas.map((area) => area.key)).toEqual(['home', 'produccion', 'combustible', 'dashboard', 'admin-center'])
    expect(areas).toHaveLength(5)
    expect(names).toContain('admin-center')
    expect(names).not.toContain('admin-crud')
    expect(new Set(names).size).toBe(names.length)
  })
})
