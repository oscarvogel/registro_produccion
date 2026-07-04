import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useConnectivityStore } from './connectivity'

const checkBackendMock = vi.fn()

vi.mock('@/services/healthCheck', () => ({
  checkBackend: (...args) => checkBackendMock(...args),
}))

function setNavigatorOnline(value) {
  Object.defineProperty(navigator, 'onLine', {
    configurable: true,
    get: () => value,
  })
}

describe('connectivity store (with healthcheck)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    setNavigatorOnline(true)
    checkBackendMock.mockReset()
  })

  afterEach(() => {
    // Tear down any store that was init()'ed in this test so window event
    // listeners do not accumulate across tests.
    const store = useConnectivityStore()
    store.teardown()
    vi.restoreAllMocks()
  })

  it('refreshBackendHealth flips isBackendUp=true on "ok"', async () => {
    checkBackendMock.mockResolvedValueOnce('ok')
    setNavigatorOnline(true)
    const store = useConnectivityStore()
    store.init()
    const result = await store.refreshBackendHealth({ force: true })
    expect(result).toBe(true)
    expect(store.isBackendUp).toBe(true)
    expect(store.lastHealthResult).toBe('ok')
    expect(store.lastBackendCheckAt).toBeGreaterThan(0)
    expect(store.pendingInitialHealthCheck).toBe(false)
  })

  it('refreshBackendHealth flips isBackendUp=false on degraded / unreachable / timeout', async () => {
    for (const state of ['degraded', 'unreachable', 'timeout']) {
      checkBackendMock.mockResolvedValueOnce(state)
      const store = useConnectivityStore()
      store.init()
      await store.refreshBackendHealth({ force: true })
      expect(store.isBackendUp).toBe(false)
      expect(store.lastHealthResult).toBe(state)
    }
  })

  it('refreshBackendHealth skips the network call when offline', async () => {
    setNavigatorOnline(false)
    const store = useConnectivityStore()
    store.init()
    const ok = await store.refreshBackendHealth({ force: true })
    expect(ok).toBe(false)
    expect(store.isBackendUp).toBe(false)
    expect(checkBackendMock).not.toHaveBeenCalled()
  })

  it('caches the healthy state within TTL and skips subsequent calls', async () => {
    checkBackendMock.mockResolvedValue('ok')
    const store = useConnectivityStore()
    store.init()
    await store.refreshBackendHealth()
    expect(checkBackendMock).toHaveBeenCalledTimes(1)
    // Cache is fresh — second call returns the cached value without hitting the API.
    await store.refreshBackendHealth()
    expect(checkBackendMock).toHaveBeenCalledTimes(1)
  })

  it('force=true ignores the cache', async () => {
    checkBackendMock.mockResolvedValue('ok')
    const store = useConnectivityStore()
    store.init()
    await store.refreshBackendHealth()
    await store.refreshBackendHealth({ force: true })
    expect(checkBackendMock).toHaveBeenCalledTimes(2)
  })

  it('flipping back to online triggers a new healthcheck', async () => {
    checkBackendMock.mockResolvedValue('ok')
    const store = useConnectivityStore()
    store.init()
    setNavigatorOnline(false)
    window.dispatchEvent(new Event('offline'))
    expect(checkBackendMock).not.toHaveBeenCalled()
    setNavigatorOnline(true)
    window.dispatchEvent(new Event('online'))
    // Drain the microtasks queued by the offline → online transition.
    for (let i = 0; i < 5; i++) await Promise.resolve()
    expect(checkBackendMock).toHaveBeenCalledTimes(1)
  })

  it('startPeriodicHealthChecks registers a setInterval with the requested period', async () => {
    const setIntervalSpy = vi.spyOn(window, 'setInterval')
    const clearIntervalSpy = vi.spyOn(window, 'clearInterval')
    checkBackendMock.mockResolvedValue('ok')
    const store = useConnectivityStore()
    store.init()
    expect(store._healthInterval ?? null).toBeNull()
    const stop = store.startPeriodicHealthChecks({ intervalMs: 500 })
    expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 500)
    expect(store._healthInterval).not.toBeNull()
    stop()
    expect(clearIntervalSpy).toHaveBeenCalled()
  })

  it('startPeriodicHealthChecks is idempotent — second call returns a no-op teardown', async () => {
    const setIntervalSpy = vi.spyOn(window, 'setInterval')
    checkBackendMock.mockResolvedValue('ok')
    const store = useConnectivityStore()
    store.init()
    const stop1 = store.startPeriodicHealthChecks({ intervalMs: 500 })
    const stop2 = store.startPeriodicHealthChecks({ intervalMs: 500 })
    expect(setIntervalSpy).toHaveBeenCalledTimes(1)
    stop1()
    stop2()
  })

  it('isOfflineOrBackendDown is true when online and backend is degraded', async () => {
    checkBackendMock.mockResolvedValueOnce('degraded')
    const store = useConnectivityStore()
    store.init()
    expect(store.isOfflineOrBackendDown).toBe(false) // before healthcheck
    await store.refreshBackendHealth({ force: true })
    expect(store.isOnline).toBe(true)
    expect(store.isBackendUp).toBe(false)
    expect(store.isOfflineOrBackendDown).toBe(true)
  })

  it('hasFreshBackendState is true right after refresh and false when the cache is older than the TTL', async () => {
    checkBackendMock.mockResolvedValueOnce('ok')
    const store = useConnectivityStore()
    store.init()
    expect(store.hasFreshBackendState).toBe(false)
    await store.refreshBackendHealth({ force: true })
    expect(store.hasFreshBackendState).toBe(true)
    // Backdate the cache to simulate TTL expiry without relying on fake timers.
    store.lastBackendCheckAt = Date.now() - 31 * 1000
    expect(store.hasFreshBackendState).toBe(false)
  })
})
