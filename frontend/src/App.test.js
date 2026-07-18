import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

const mocks = vi.hoisted(() => ({
  route: {
    name: 'home',
    fullPath: '/',
    params: {},
  },
  routerPush: vi.fn(),
  logout: vi.fn(),
  refreshPendingCount: vi.fn(),
  syncPending: vi.fn(),
  toggleTheme: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => mocks.route,
  useRouter: () => ({ push: mocks.routerPush }),
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    isAuthenticated: true,
    isAuthenticatedOffline: false,
    isAdmin: true,
    user: { nombre: 'Admin User', is_admin: 1, encargado: 1 },
    userName: 'Admin User',
    cachedSession: null,
    logout: mocks.logout,
  }),
}))

vi.mock('@/stores/produccion', () => ({
  useProduccionStore: () => ({
    pendingCount: 2,
    refreshPendingCount: mocks.refreshPendingCount,
    syncPending: mocks.syncPending,
  }),
}))

vi.mock('@/stores/connectivity', () => ({
  useConnectivityStore: () => ({
    isOffline: false,
    isOnline: true,
  }),
}))

vi.mock('@/composables/useTheme', () => ({
  useTheme: () => ({
    isDark: { value: true },
    toggleTheme: mocks.toggleTheme,
  }),
}))

function mountApp() {
  return mount(App, {
    global: {
      directives: {
        motionPage: {},
      },
      stubs: {
        AppIcon: { template: '<span class="icon-stub" />' },
        OfflineBanner: { template: '<div />' },
        ToastHost: { template: '<div />' },
        RouterLink: {
          props: ['to'],
          template: '<a href="#" :data-route="to.name"><slot /></a>',
        },
        RouterView: {
          template: '<div><slot :Component="component" :route="viewRoute" /></div>',
          data: () => ({
            component: null,
            viewRoute: { fullPath: '/' },
          }),
        },
      },
    },
  })
}

function sectionButton(wrapper, label) {
  return wrapper.findAll('nav button').find((button) => button.text().trim() === label)
}

describe('App navigation shell', () => {
  let wrapper

  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('keeps only one accordion section open', async () => {
    wrapper = mountApp()

    const production = sectionButton(wrapper, 'Producción')
    const dashboard = sectionButton(wrapper, 'Dashboard')

    await production.trigger('click')
    expect(production.attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('#sidebar-section-produccion').isVisible()).toBe(true)

    await dashboard.trigger('click')
    expect(production.attributes('aria-expanded')).toBe('false')
    expect(dashboard.attributes('aria-expanded')).toBe('true')
    expect(wrapper.get('#sidebar-section-dashboard').isVisible()).toBe(true)
  })

  it('hides section children when the desktop sidebar is collapsed', async () => {
    wrapper = mountApp()

    const production = sectionButton(wrapper, 'Producción')
    await production.trigger('click')
    await wrapper.get('button[aria-label="Contraer navegacion"]').trigger('click')

    expect(production.attributes('aria-expanded')).toBe('false')
    expect(wrapper.get('#sidebar-section-produccion').isVisible()).toBe(false)
    expect(wrapper.get('button[aria-label="Expandir navegacion"]')).toBeTruthy()
    expect(localStorage.getItem('sidebarCollapsed')).toBe('1')
  })

  it('closes the mobile drawer after navigating', async () => {
    wrapper = mountApp()

    await wrapper.get('button[aria-label="Abrir navegacion"]').trigger('click')
    expect(wrapper.get('aside').classes()).toContain('translate-x-0')
    expect(wrapper.find('.fixed.inset-0.z-40').exists()).toBe(true)

    await wrapper.get('[data-route="home"]').trigger('click')
    expect(wrapper.get('aside').classes()).toContain('-translate-x-full')
    expect(wrapper.find('.fixed.inset-0.z-40').exists()).toBe(false)
  })
})
