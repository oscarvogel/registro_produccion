import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/components/ui/AppIcon.vue', () => ({
  default: { name: 'AppIcon', template: '<i class="icon-stub" />' },
}))

import OfflineBanner from './OfflineBanner.vue'
import { useConnectivityStore } from '@/stores/connectivity'

function setNavigatorOnline(value) {
  Object.defineProperty(navigator, 'onLine', {
    configurable: true,
    get: () => value,
  })
}

describe('OfflineBanner copy', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setNavigatorOnline(true)
  })

  afterEach(() => {
    setNavigatorOnline(true)
  })

  it('is hidden when online', () => {
    const store = useConnectivityStore()
    store.init()
    const wrapper = mount(OfflineBanner, { props: { hasCachedSession: true } })
    expect(wrapper.find('[data-testid="offline-banner"]').exists()).toBe(false)
  })

  it('shows the reassuring copy when the operator already has a cached session', () => {
    const store = useConnectivityStore()
    setNavigatorOnline(false)
    store.init()
    const wrapper = mount(OfflineBanner, { props: { hasCachedSession: true } })
    const banner = wrapper.find('[data-testid="offline-banner"]')
    expect(banner.exists()).toBe(true)
    expect(banner.text()).toContain('Sin conexión')
    expect(banner.text()).not.toContain('primera vez')
    expect(banner.text()).not.toContain('14 días')
  })

  it('explains the first-time requirement when the operator has no cached session', () => {
    const store = useConnectivityStore()
    setNavigatorOnline(false)
    store.init()
    const wrapper = mount(OfflineBanner, { props: { hasCachedSession: false } })
    const banner = wrapper.find('[data-testid="offline-banner"]')
    expect(banner.exists()).toBe(true)
    expect(banner.text()).toContain('Sin conexión')
    expect(banner.text()).toContain('primera vez')
    expect(banner.text()).toContain('14 días')
    expect(banner.text()).toContain('guardar tu sesión')
  })

  it('honors an explicit message override', () => {
    const store = useConnectivityStore()
    setNavigatorOnline(false)
    store.init()
    const wrapper = mount(OfflineBanner, {
      props: { hasCachedSession: false, message: 'CUSTOM' },
    })
    expect(wrapper.text()).toContain('CUSTOM')
  })

  it('renders the pending counter when offline and pendingCount > 0', () => {
    const store = useConnectivityStore()
    setNavigatorOnline(false)
    store.init()
    const wrapper = mount(OfflineBanner, {
      props: { hasCachedSession: true, pendingCount: 3 },
    })
    expect(wrapper.find('[data-testid="offline-banner-pending"]').text()).toContain('3')
    expect(wrapper.find('[data-testid="offline-banner-pending"]').text()).toContain('pendientes')
  })

  it('uses singular "pendiente" when pendingCount is 1', () => {
    const store = useConnectivityStore()
    setNavigatorOnline(false)
    store.init()
    const wrapper = mount(OfflineBanner, {
      props: { hasCachedSession: true, pendingCount: 1 },
    })
    expect(wrapper.find('[data-testid="offline-banner-pending"]').text()).toContain('1 pendiente')
    expect(wrapper.find('[data-testid="offline-banner-pending"]').text()).not.toContain(
      'pendientes',
    )
  })

  it('keeps amber background when only internet is down', () => {
    const store = useConnectivityStore()
    setNavigatorOnline(false)
    store.init()
    const wrapper = mount(OfflineBanner, { props: { hasCachedSession: true } })
    expect(wrapper.find('[data-testid="offline-banner"]').classes().join(' ')).toContain(
      'bg-amber-500',
    )
  })

  // Note: the "server unreachable but online" red-banner branch is exercised
  // by the production code via `connectivity.isBackendUp === false`, but the
  // banner is currently hidden when `isOnline === true` because that signal
  // is meaningful only once #49 (real healthcheck) is in place. We do not
  // assert that path here to keep this test independent of that work.
})
