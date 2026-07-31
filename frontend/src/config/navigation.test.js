import { describe, expect, it } from 'vitest'

import { createSidebarNavigation, flattenNavigation } from './navigation'

function routeNames(navigation) {
  return flattenNavigation(navigation).map((item) => item.to.name)
}

describe('role-aware sidebar navigation', () => {
  it('keeps operator navigation compact and without administrative routes', () => {
    const navigation = createSidebarNavigation({ pendingCount: 3 })

    expect(navigation.primaryItems.map((item) => item.key)).toEqual(['home', 'manuales'])
    expect(navigation.sections.map((section) => section.key)).toEqual(['combustible', 'produccion'])
    expect(routeNames(navigation)).not.toContain('admin-center')
    expect(routeNames(navigation)).not.toContain('admin-crud')
    expect(navigation.sections[1].items[1].badge).toBe(3)
  })

  it('shows the operational dashboard but not personal records to an encargado', () => {
    const navigation = createSidebarNavigation({ isEncargado: true })

    expect(navigation.sections.map((section) => section.key)).toEqual([
      'operacion',
      'combustible',
      'produccion',
    ])
    expect(routeNames(navigation)).toContain('dashboard')
    expect(routeNames(navigation)).not.toContain('mis-registros')
  })

  it('routes administrative management through one center without duplicated CRUD links', () => {
    const navigation = createSidebarNavigation({ isAdmin: true, isEncargado: true })
    const names = routeNames(navigation)
    const adminItem = navigation.trailingItems.find((item) => item.key === 'admin-center')

    expect(adminItem.to.name).toBe('admin-center')
    expect(navigation.primaryItems.map((item) => item.key)).toEqual(['home', 'manuales'])
    expect(navigation.trailingItems.map((item) => item.key)).toEqual(['admin-center'])
    expect(adminItem.activeRoutes).toEqual([
      'admin-center',
      'admin-crud',
      'admin-configuracion',
    ])
    expect(names).toContain('admin-dashboard')
    expect(names).not.toContain('admin-crud')
    expect(new Set(names).size).toBe(names.length)
  })
})
