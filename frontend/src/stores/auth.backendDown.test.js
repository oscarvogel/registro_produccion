import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    defaults: { headers: { common: {} } },
  },
}))

import api from '@/services/api'
import {
  hashSecret,
  useAuthStore,
  LOGIN_ERROR_BAD_CREDENTIALS,
  LOGIN_ERROR_SERVER,
} from './auth'

const CACHE_KEY = 'offline_session_cache'
const user = { idPersonal: 7, dni: '12345678', nombre: 'Operador', is_admin: 0 }

async function seedFreshCache(password = 'secreto') {
  localStorage.setItem(
    CACHE_KEY,
    JSON.stringify({
      user,
      passwordHash: await hashSecret(password),
      cachedAt: Date.now(),
    }),
  )
}

describe('auth store / fallback offline cuando backend esta caido', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
    delete api.defaults.headers.common.Authorization
  })

  it('entra con la sesion local si MySQL/backend responde 500', async () => {
    await seedFreshCache()
    api.post.mockRejectedValueOnce({
      response: { status: 500, data: { detail: 'MySQL unavailable' } },
    })

    const store = useAuthStore()
    const ok = await store.login('12345678', 'secreto')

    expect(ok).toBe(true)
    expect(store.offlineMode).toBe(true)
    expect(store.isAuthenticatedOffline).toBe(true)
    expect(store.user).toEqual(user)
    expect(store.error).toBeNull()
  })

  it('entra con la sesion local si la request no obtiene respuesta', async () => {
    await seedFreshCache()
    api.post.mockRejectedValueOnce({ message: 'Network Error' })

    const store = useAuthStore()
    const ok = await store.login('12345678', 'secreto')

    expect(ok).toBe(true)
    expect(store.offlineMode).toBe(true)
  })

  it('no usa cache si el servidor responde 401', async () => {
    await seedFreshCache()
    api.post.mockRejectedValueOnce({
      response: { status: 401, data: { detail: 'invalid credentials' } },
    })

    const store = useAuthStore()
    const ok = await store.login('12345678', 'secreto')

    expect(ok).toBe(false)
    expect(store.offlineMode).toBe(false)
    expect(store.error).toBe(LOGIN_ERROR_BAD_CREDENTIALS)
  })

  it('no permite fallback con password distinta a la cacheada', async () => {
    await seedFreshCache('correcta')
    api.post.mockRejectedValueOnce({ response: { status: 503, data: {} } })

    const store = useAuthStore()
    const ok = await store.login('12345678', 'incorrecta')

    expect(ok).toBe(false)
    expect(store.offlineMode).toBe(false)
    expect(store.error).toBe(LOGIN_ERROR_SERVER)
  })

  it('no permite fallback con DNI distinto al cacheado', async () => {
    await seedFreshCache()
    api.post.mockRejectedValueOnce({ response: { status: 503, data: {} } })

    const store = useAuthStore()
    const ok = await store.login('99999999', 'secreto')

    expect(ok).toBe(false)
    expect(store.offlineMode).toBe(false)
    expect(store.error).toBe(LOGIN_ERROR_SERVER)
  })
})
