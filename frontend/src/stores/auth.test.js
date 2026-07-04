import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    defaults: { headers: { common: {} } },
  },
}))

import api from '@/services/api'
import {
  useAuthStore,
  hashSecret,
  clearOfflineSessionCache,
  readOfflineSessionCache,
  readOfflineGracePeriodDays,
  classifyLoginError,
  LOGIN_ERROR_BAD_CREDENTIALS,
  LOGIN_ERROR_NO_CONNECTION,
  LOGIN_ERROR_SERVER,
} from './auth'

const CACHE_KEY = 'offline_session_cache'

function fakeJwt(expSecondsFromNow) {
  const header = btoa(JSON.stringify({ alg: 'none', typ: 'JWT' })).replace(/=+$/, '')
  const payload = btoa(
    JSON.stringify({ sub: '1', dni: '12345678', exp: expSecondsFromNow }),
  ).replace(/=+$/, '')
  // header.payload.signature — match production JWT layout
  return `${header}.${payload}.sig`
}

function seedValidToken(state) {
  const token = fakeJwt(Math.floor(Date.now() / 1000) + 3600)
  state.token = token
  localStorage.setItem('token', token)
}

function seedUser(state) {
  const user = { idPersonal: 7, dni: '12345678', nombre: 'Operador', is_admin: 0 }
  state.user = user
  localStorage.setItem('user', JSON.stringify(user))
}

function seedCache(user, cachedAt, passwordHash = 'hash-x') {
  const payload = { user, passwordHash, cachedAt }
  localStorage.setItem(CACHE_KEY, JSON.stringify(payload))
  return payload
}

describe('auth store / initAuth offline', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('hashSecret returns a stable non-empty string', async () => {
    const a = await hashSecret('secreto')
    const b = await hashSecret('secreto')
    expect(a).toBeTruthy()
    expect(a).toBe(b)
    expect((await hashSecret('secreto')) !== (await hashSecret('otro'))).toBe(true)
  })

  it('returns "online" when the JWT is still valid', () => {
    const store = useAuthStore()
    seedValidToken(store)
    seedUser(store)
    const mode = store.initAuth()
    expect(mode).toBe('online')
    expect(store.isAuthenticated).toBe(true)
    expect(store.offlineMode).toBe(false)
  })

  it('returns "login-required" when online but token expired', () => {
    const store = useAuthStore()
    seedValidToken(store)
    store.token = fakeJwt(Math.floor(Date.now() / 1000) - 60)
    localStorage.setItem('token', store.token)
    // navigator.onLine is true in jsdom by default
    const mode = store.initAuth()
    expect(mode).toBe('login-required')
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
  })

  it('returns "offline" when offline + fresh cache restores the user', () => {
    const user = { idPersonal: 7, dni: '12345678', nombre: 'Operador', is_admin: 0 }
    seedCache(user, Date.now() - 1000) // 1 segundo de antigüedad
    const original = navigator.onLine
    Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => false })
    try {
      const store = useAuthStore()
      const mode = store.initAuth()
      expect(mode).toBe('offline')
      expect(store.offlineMode).toBe(true)
      expect(store.user).toEqual(user)
      expect(store.isAuthenticatedOffline).toBe(true)
    } finally {
      Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => original })
    }
  })

  it('returns "offline-locked" when offline and cache is past the grace period', () => {
    const user = { idPersonal: 7, dni: '12345678', nombre: 'Operador', is_admin: 0 }
    const grace = readOfflineGracePeriodDays()
    seedCache(user, Date.now() - (grace + 1) * 24 * 60 * 60 * 1000)
    const original = navigator.onLine
    Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => false })
    try {
      const store = useAuthStore()
      const mode = store.initAuth()
      expect(mode).toBe('offline-locked')
      expect(store.offlineMode).toBe(false)
      expect(store.user).toBeNull()
    } finally {
      Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => original })
    }
  })

  it('offline cache helpers read/write the storage payload', () => {
    const user = { idPersonal: 1, dni: '99999999', nombre: 'X' }
    seedCache(user, Date.now())
    const cached = readOfflineSessionCache()
    expect(cached?.user.dni).toBe('99999999')
    clearOfflineSessionCache()
    expect(readOfflineSessionCache()).toBeNull()
  })

  it('cacheSession writes a payload after a successful online login', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        access_token: fakeJwt(Math.floor(Date.now() / 1000) + 3600),
        user: { idPersonal: 9, dni: '11111111', nombre: 'Nuevo', is_admin: 0 },
      },
    })
    const store = useAuthStore()
    const ok = await store.login('11111111', 'contraseña')
    expect(ok).toBe(true)
    const cached = readOfflineSessionCache()
    expect(cached?.user.dni).toBe('11111111')
    expect(cached?.passwordHash).toBeTruthy()
    expect(typeof cached?.cachedAt).toBe('number')
  })

  it('logout keeps the offline cache so the operator can come back', () => {
    const user = { idPersonal: 1, dni: '88888888', nombre: 'Op' }
    seedCache(user, Date.now())
    const store = useAuthStore()
    store.logout()
    // token/user are cleared
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    // but the cache stays so they can re-enter offline within the grace period
    const cached = readOfflineSessionCache()
    expect(cached?.user.dni).toBe('88888888')
  })

  it('clearOfflineCache removes the cache as well', () => {
    const user = { idPersonal: 1, dni: '77777777', nombre: 'Op' }
    seedCache(user, Date.now())
    const store = useAuthStore()
    store.clearOfflineCache()
    expect(readOfflineSessionCache()).toBeNull()
    expect(store.cachedSession).toBeNull()
  })

  it('isOfflineCacheValid respects the configured grace period', () => {
    const user = { idPersonal: 1, dni: '66666666', nombre: 'Op' }
    seedCache(user, Date.now())
    const store = useAuthStore()
    expect(store.isOfflineCacheValid()).toBe(true)
    // age the cache past the grace period
    store.cachedSession.cachedAt = Date.now() - (readOfflineGracePeriodDays() + 2) * 24 * 3600 * 1000
    expect(store.isOfflineCacheValid()).toBe(false)
  })
})

describe('auth store / login error messages', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('shows specific message for 401 credentials', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 401, data: { detail: 'whatever' } } })
    const store = useAuthStore()
    const ok = await store.login('12345678', 'wrong')
    expect(ok).toBe(false)
    expect(store.error).toBe(LOGIN_ERROR_BAD_CREDENTIALS)
  })

  it('keeps generic connection error for non-401 failures', async () => {
    api.post.mockRejectedValueOnce({ response: { status: 500, data: { detail: 'pymysql garbage' } } })
    const store = useAuthStore()
    const ok = await store.login('12345678', 'whatever')
    expect(ok).toBe(false)
    // The store keeps its non-leaky message even when backend returns garbage.
    expect(store.error).toBe(LOGIN_ERROR_SERVER)
    expect(store.error).not.toMatch(/pymysql/i)
  })

  it('uses the no-connection message when axios has no response (offline)', async () => {
    api.post.mockRejectedValueOnce({ message: 'Network Error' })
    const store = useAuthStore()
    const ok = await store.login('12345678', 'whatever')
    expect(ok).toBe(false)
    expect(store.error).toBe(LOGIN_ERROR_NO_CONNECTION)
  })

  it('passes _suppressErrorToast: true on the login request', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        access_token: fakeJwt(Math.floor(Date.now() / 1000) + 3600),
        user: { idPersonal: 1, dni: '1', nombre: 'X', is_admin: 0 },
      },
    })
    const store = useAuthStore()
    await store.login('1', 'p')
    expect(api.post).toHaveBeenCalledWith(
      '/api/auth/login',
      { dni: '1', password: 'p' },
      expect.objectContaining({ _suppressErrorToast: true }),
    )
  })

  it('uses backend detail on 4xx only when detail is short and non-technical', async () => {
    api.post.mockRejectedValueOnce({
      response: { status: 400, data: { detail: 'La contrasena es muy corta' } },
    })
    const store = useAuthStore()
    await store.login('1', 'x')
    expect(store.error).toBe('La contrasena es muy corta')
  })

  it('rejects technical-looking 4xx details to avoid leaks', async () => {
    api.post.mockRejectedValueOnce({
      response: {
        status: 400,
        data: {
          detail:
            "pymysql.err.OperationalError: (2013, 'Lost connection to MySQL server')",
        },
      },
    })
    const store = useAuthStore()
    await store.login('1', 'x')
    expect(store.error).toBe(LOGIN_ERROR_SERVER)
    expect(store.error).not.toMatch(/pymysql/i)
  })
})

describe('classifyLoginError', () => {
  it('returns no-connection when there is no response object', () => {
    expect(classifyLoginError({ message: 'Network Error' })).toBe(
      LOGIN_ERROR_NO_CONNECTION,
    )
    expect(classifyLoginError(null)).toBe(LOGIN_ERROR_SERVER)
  })

  it('returns bad-credentials for 401', () => {
    expect(
      classifyLoginError({ response: { status: 401, data: { detail: 'X' } } }),
    ).toBe(LOGIN_ERROR_BAD_CREDENTIALS)
  })

  it('returns server for 5xx and never echoes detail', () => {
    expect(
      classifyLoginError({
        response: {
          status: 503,
          data: { detail: "SELECT * FROM usuarios WHERE password_hash = 'x'" },
        },
      }),
    ).toBe(LOGIN_ERROR_SERVER)
  })

  it('echoes backend detail on 4xx only when it looks user-friendly', () => {
    expect(
      classifyLoginError({
        response: { status: 400, data: { detail: 'DNI invalido' } },
      }),
    ).toBe('DNI invalido')
  })

  it('ignores overly long backend detail to avoid weird UI', () => {
    const huge = 'x'.repeat(200)
    expect(
      classifyLoginError({ response: { status: 400, data: { detail: huge } } }),
    ).toBe(LOGIN_ERROR_SERVER)
  })

  it('ignores technical-looking strings even when short', () => {
    expect(
      classifyLoginError({
        response: {
          status: 400,
          data: { detail: 'INSERT INTO foo (password_hash) VALUES (1)' },
        },
      }),
    ).toBe(LOGIN_ERROR_SERVER)
  })
})
