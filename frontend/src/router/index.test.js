import { describe, expect, it } from 'vitest'

import router, { authorizeRoute } from './index'

describe('admin center route', () => {
  it('is registered as an administrator-only route', () => {
    const resolved = router.resolve({ name: 'admin-center' })
    const adminRoot = router.getRoutes().find((route) => route.path === '/admin')

    expect(resolved.path).toBe('/admin/gestion')
    expect(resolved.meta.requiresAuth).toBe(true)
    expect(resolved.meta.requiresAdmin).toBe(true)
    expect(adminRoot.redirect).toEqual({ name: 'admin-center' })
  })

  it('redirects a non-admin user away from the admin center', () => {
    const to = router.resolve({ name: 'admin-center' })
    const authStore = {
      isAuthenticated: true,
      isAuthenticatedOffline: false,
      user: { is_admin: 0, encargado: 0 },
    }

    expect(authorizeRoute(to, authStore)).toEqual({ name: 'home' })
  })

  it('allows an authenticated administrator into the admin center', () => {
    const to = router.resolve({ name: 'admin-center' })
    const authStore = {
      isAuthenticated: true,
      isAuthenticatedOffline: false,
      user: { is_admin: 1, encargado: 0 },
    }

    expect(authorizeRoute(to, authStore)).toBe(true)
  })
})
