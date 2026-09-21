import { describe, expect, it } from 'vitest'

import {
  createMobileMoreGroups,
  createMobileNavigation,
  createSidebarNavigation,
  flattenNavigation,
  isNavigationItemActive,
  shouldShowMobileBottomNavigation,
} from './navigation'

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

  it('assigns a distinct themed icon key to each navigation responsibility', () => {
    const navigation = createSidebarNavigation({ isAdmin: true, isEncargado: true })
    const items = flattenNavigation(navigation)

    expect(navigation.sections.map((section) => section.icon)).toEqual([
      'tracking',
      'fuel',
      'production',
    ])
    expect(items.find((item) => item.key === 'admin-dashboard').icon).toBe('analysis')
    expect(items.find((item) => item.key === 'carga-combustible').icon).toBe('fuel-add')
    expect(items.find((item) => item.key === 'carga-produccion').icon).toBe('production-add')
  })
})

describe('role-aware mobile navigation', () => {
  it('keeps the operator quick actions and pending count', () => {
    const items = createMobileNavigation({ pendingCount: 7 })

    expect(items.map((item) => item.key)).toEqual([
      'home',
      'carga-produccion',
      'carga-combustible',
      'pendientes',
    ])
    expect(items[3].badge).toBe(7)
  })

  it('prioritizes operational follow-up for encargados', () => {
    const items = createMobileNavigation({ isEncargado: true })

    expect(items.map((item) => item.key)).toEqual([
      'home',
      'dashboard',
      'carga-produccion',
      'pendientes',
    ])
  })

  it('prioritizes analytics and administration for admins', () => {
    const items = createMobileNavigation({ isAdmin: true })

    expect(items.map((item) => item.key)).toEqual([
      'home',
      'dashboard',
      'admin-dashboard',
      'admin-center',
    ])
    expect(items[2].mobileLabel).toBe('Análisis')
    expect(items[3].accessibleLabel).toBe('Administración')
  })

  it('uses admin destinations when both admin and encargado flags are set', () => {
    expect(createMobileNavigation({ isAdmin: true, isEncargado: true }).map((item) => item.key)).toEqual([
      'home',
      'dashboard',
      'admin-dashboard',
      'admin-center',
    ])
  })
})

describe('mobile More destinations', () => {
  it('shows operator destinations not already present in the bottom bar', () => {
    const groups = createMobileMoreGroups({ pendingCount: 4 })

    expect(groups.map((group) => [group.key, group.items.map((item) => item.key)])).toEqual([
      ['general', ['manuales']],
      ['produccion', ['mis-registros']],
    ])
  })

  it('keeps secondary destinations and the pending badge available for encargados and admins', () => {
    const encargadoGroups = createMobileMoreGroups({ isEncargado: true })
    const adminGroups = createMobileMoreGroups({ isAdmin: true, pendingCount: 6 })
    const encargadoKeys = encargadoGroups.flatMap((group) => group.items.map((item) => item.key))
    const adminItems = adminGroups.flatMap((group) => group.items)

    expect(encargadoKeys).toEqual(['manuales', 'carga-combustible'])
    expect(adminItems.map((item) => item.key)).toEqual([
      'manuales',
      'carga-combustible',
      'carga-produccion',
      'pendientes',
      'mis-registros',
    ])
    expect(adminItems.find((item) => item.key === 'pendientes').badge).toBe(6)
  })

  it.each([
    [{}, 'operator'],
    [{ isEncargado: true }, 'encargado'],
    [{ isAdmin: true }, 'admin'],
  ])('does not duplicate direct destinations for the %s role', (options) => {
    const directKeys = createMobileNavigation(options).map((item) => item.key)
    const moreKeys = createMobileMoreGroups(options).flatMap((group) => group.items.map((item) => item.key))
    const directRoutes = createMobileNavigation(options).map((item) => item.to.name)
    const moreRoutes = createMobileMoreGroups(options).flatMap((group) => group.items.map((item) => item.to.name))

    expect(moreKeys.some((key) => directKeys.includes(key))).toBe(false)
    expect(new Set(moreKeys).size).toBe(moreKeys.length)
    expect([...directRoutes, ...moreRoutes].sort()).toEqual(routeNames(createSidebarNavigation(options)).sort())
  })
})

describe('active navigation destinations', () => {
  it('recognizes child routes of the operational dashboard', () => {
    const dashboardItem = createMobileNavigation({ isEncargado: true })
      .find((item) => item.key === 'dashboard')

    expect(isNavigationItemActive(dashboardItem, { name: 'dashboard-registros', params: {} })).toBe(true)
  })

  it('recognizes routes grouped under administration', () => {
    const adminItem = createMobileNavigation({ isAdmin: true })
      .find((item) => item.key === 'admin-center')

    expect(isNavigationItemActive(adminItem, { name: 'admin-crud', params: { entity: 'equipos' } })).toBe(true)
  })
})

describe('mobile bottom navigation visibility', () => {
  it('leaves room for the fixed action bar in production and fuel forms', () => {
    expect(shouldShowMobileBottomNavigation('produccion')).toBe(false)
    expect(shouldShowMobileBottomNavigation('combustible')).toBe(false)
    expect(shouldShowMobileBottomNavigation('home')).toBe(true)
    expect(shouldShowMobileBottomNavigation('manuales')).toBe(true)
  })
})
