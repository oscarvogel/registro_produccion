import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useConnectivityStore } from './connectivity'

function setNavigatorOnline(value) {
  Object.defineProperty(navigator, 'onLine', {
    configurable: true,
    get: () => value,
  })
}

describe('connectivity store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setNavigatorOnline(true)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('reads navigator.onLine on first init', () => {
    setNavigatorOnline(true)
    const store = useConnectivityStore()
    store.init()
    expect(store.isOnline).toBe(true)
    expect(store.isOffline).toBe(false)
  })

  it('starts offline if the navigator reported offline', () => {
    setNavigatorOnline(false)
    const store = useConnectivityStore()
    store.init()
    expect(store.isOnline).toBe(false)
    expect(store.isBackendUp).toBe(false) // implicit when offline
  })

  it('flips to offline when an offline event fires', () => {
    const store = useConnectivityStore()
    store.init()
    expect(store.isOnline).toBe(true)
    window.dispatchEvent(new Event('offline'))
    expect(store.isOnline).toBe(false)
    expect(store.isBackendUp).toBe(false)
  })

  it('flips back to online when an online event fires', () => {
    setNavigatorOnline(false)
    const store = useConnectivityStore()
    store.init()
    expect(store.isOnline).toBe(false)
    setNavigatorOnline(true)
    window.dispatchEvent(new Event('online'))
    expect(store.isOnline).toBe(true)
    // Coming back online is an optimistic assumption that the backend is up.
    expect(store.isBackendUp).toBe(true)
    expect(store.lastBackendCheckAt).toBeGreaterThan(0)
  })

  it('does not register listeners more than once', () => {
    const store = useConnectivityStore()
    store.init()
    store.init() // should be a no-op
    setNavigatorOnline(false)
    // Only one listener means the state flips once, not twice.
    window.dispatchEvent(new Event('offline'))
    expect(store.isOnline).toBe(false)
  })

  it('safely does nothing in non-browser environments', () => {
    const originalWindow = globalThis.window
    // simulate SSR
    // @ts-expect-error - intentional
    delete globalThis.window
    try {
      const store = useConnectivityStore()
      expect(() => store.init()).not.toThrow()
    } finally {
      globalThis.window = originalWindow
    }
  })
})
