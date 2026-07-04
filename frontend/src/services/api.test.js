import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const toastError = vi.fn()
const toastInfo = vi.fn()
const toastSuccess = vi.fn()

vi.mock('@/stores/toast', () => ({
  useToastStore: () => ({
    error: toastError,
    info: toastInfo,
    success: toastSuccess,
  }),
}))

// Connectivity is mocked per test. Defaults to "online" so existing cases don't
// need to set it; the few tests that need an offline scenario set
// `currentConnectivityOffline = true` before driving the handler.
let currentConnectivityOffline = false

vi.mock('@/stores/connectivity', () => ({
  useConnectivityStore: () => ({
    get isOffline() {
      return currentConnectivityOffline
    },
    get isOnline() {
      return !currentConnectivityOffline
    },
    get isOfflineOrBackendDown() {
      return currentConnectivityOffline
    },
  }),
}))

// Capture the response interceptor's error handler so tests can drive it
// without spinning up a real HTTP request. Each test gets a fresh fn.
const capturedHandlers = []

vi.mock('axios', async () => {
  const actual = await vi.importActual('axios')
  return {
    ...actual,
    default: {
      ...actual.default,
      create: () => {
        const requestUse = vi.fn()
        const responseUse = vi.fn((ok, err) => {
          if (typeof err === 'function') capturedHandlers.push(err)
        })
        return {
          interceptors: {
            request: { use: requestUse },
            response: { use: responseUse },
          },
          defaults: { headers: { common: {} } },
          post: vi.fn(),
          get: vi.fn(),
          put: vi.fn(),
          delete: vi.fn(),
          request: vi.fn(),
        }
      },
    },
  }
})

import axios from 'axios'

let cachedApi
let cachedHandler

beforeAll(async () => {
  cachedApi = await import('./api')
  cachedHandler = capturedHandlers[capturedHandlers.length - 1]
  expect(typeof cachedHandler).toBe('function')
})

async function loadApi() {
  return cachedApi
}

async function getErrorHandler() {
  return cachedHandler
}

beforeEach(() => {
  toastError.mockReset()
  toastInfo.mockReset()
  toastSuccess.mockReset()
  localStorage.clear()
  currentConnectivityOffline = false
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('normalizeBaseURL', () => {
  it('uses relative URLs when no base URL is configured', async () => {
    const { normalizeBaseURL } = await loadApi()
    expect(normalizeBaseURL()).toBe('')
    expect(normalizeBaseURL('')).toBe('')
  })

  it('removes a trailing api segment from configured base URLs', async () => {
    const { normalizeBaseURL } = await loadApi()
    expect(normalizeBaseURL('/api')).toBe('')
    expect(normalizeBaseURL('/api/')).toBe('')
    expect(normalizeBaseURL('https://example.com/api')).toBe('https://example.com')
  })

  it('keeps non-api base URLs unchanged', async () => {
    const { normalizeBaseURL } = await loadApi()
    expect(normalizeBaseURL('http://localhost:8000')).toBe('http://localhost:8000')
  })
})

describe('server error toast message', () => {
  it('uses a generic message instead of backend details for 5xx errors', async () => {
    const { SERVER_ERROR_MESSAGE } = await loadApi()
    const technicalDetail = `
      pymysql.err.OperationalError: (2013, 'Lost connection to MySQL server during query')
      SELECT id, dni, password_hash FROM usuarios WHERE dni = %s
    `

    expect(SERVER_ERROR_MESSAGE).toBe(
      'No se pudo conectar con el servidor. Intenta nuevamente en unos minutos.',
    )
    expect(SERVER_ERROR_MESSAGE).not.toContain(technicalDetail)
    expect(SERVER_ERROR_MESSAGE).not.toMatch(
      /pymysql|OperationalError|SELECT|usuarios|password_hash/i,
    )
  })
})

describe('api response interceptor', () => {
  it('uses SERVER_ERROR_MESSAGE for 5xx and never echoes technical detail', async () => {
    const handler = await getErrorHandler()
    const error = {
      response: {
        status: 500,
        data: {
          detail:
            "pymysql.err.OperationalError: (2013, 'Lost connection') SELECT * FROM usuarios",
        },
      },
      config: { url: '/api/produccion' },
    }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).toHaveBeenCalledTimes(1)
    const [, message] = toastError.mock.calls[0]
    expect(message).not.toMatch(/pymysql|SELECT|usuarios|OperationalError/i)
    expect(message).toBe(
      'No se pudo conectar con el servidor. Intenta nuevamente en unos minutos.',
    )
  })

  it('suppresses the toast when _suppressErrorToast is true on the request config', async () => {
    const handler = await getErrorHandler()
    const error = {
      response: {
        status: 500,
        data: { detail: 'something technical that should NOT leak' },
      },
      config: { url: '/api/auth/login', _suppressErrorToast: true },
    }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).not.toHaveBeenCalled()
  })

  it('shows a "no response" toast when the request failed without a response', async () => {
    const handler = await getErrorHandler()
    const error = { message: 'Network Error', config: { url: '/api/x' } }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).toHaveBeenCalledTimes(1)
    expect(toastError.mock.calls[0][0]).toBe('Backend no disponible')
  })

  it('still cleans up auth state on 401 for non-login requests', async () => {
    const handler = await getErrorHandler()
    const error = {
      response: { status: 401, data: { detail: 'expired' } },
      config: { url: '/api/produccion' },
    }
    localStorage.setItem('token', 'old-token')
    localStorage.setItem('user', JSON.stringify({ dni: 'X' }))
    await expect(handler(error)).rejects.toBe(error)
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('runs setUnauthorizedHandler when handler is configured', async () => {
    const { setUnauthorizedHandler } = await loadApi()
    const cb = vi.fn()
    setUnauthorizedHandler(cb)
    const handler = await getErrorHandler()
    const error = {
      response: { status: 401, data: { detail: 'expired' } },
      config: { url: '/api/produccion' },
    }
    await expect(handler(error)).rejects.toBe(error)
    expect(cb).toHaveBeenCalledTimes(1)
  })

  it('does NOT clear auth on 401 when request is /api/auth/login', async () => {
    const handler = await getErrorHandler()
    const error = {
      response: { status: 401, data: { detail: 'bad creds' } },
      config: { url: '/api/auth/login' },
    }
    localStorage.setItem('token', 'valid')
    localStorage.setItem('user', JSON.stringify({ dni: 'X' }))
    await expect(handler(error)).rejects.toBe(error)
    expect(localStorage.getItem('token')).toBe('valid')
  })

  it('shows the "no response" toast when the request fails without a response AND we are online', async () => {
    currentConnectivityOffline = false
    const handler = await getErrorHandler()
    const error = { message: 'Network Error', config: { url: '/api/x' } }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).toHaveBeenCalledTimes(1)
    expect(toastError.mock.calls[0][0]).toBe('Backend no disponible')
  })

  it('stays silent on network errors while offline (the amber banner has it covered)', async () => {
    currentConnectivityOffline = true
    const handler = await getErrorHandler()
    const error = { message: 'Network Error', config: { url: '/api/produccion' } }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).not.toHaveBeenCalled()
  })

  it('stays silent when navigator.onLine is false even if the connectivity store is not yet updated', async () => {
    // Simulate the race: the periodic healthcheck has not yet flipped the
    // store, but navigator already knows the network is gone.
    currentConnectivityOffline = false
    const original = navigator.onLine
    Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => false })
    try {
      const handler = await getErrorHandler()
      const error = { message: 'Network Error', config: { url: '/api/produccion' } }
      await expect(handler(error)).rejects.toBe(error)
      expect(toastError).not.toHaveBeenCalled()
    } finally {
      Object.defineProperty(navigator, 'onLine', { configurable: true, get: () => original })
    }
  })

  it('still shows 5xx toasts even when offline (operationally important)', async () => {
    // Offline + online both warrant a generic 5xx toast: the request reached
    // a server that is sick, which deserves attention regardless of the
    // amber banner.
    currentConnectivityOffline = true
    const handler = await getErrorHandler()
    const error = {
      response: { status: 500, data: { detail: 'pymysql garbage' } },
      config: { url: '/api/produccion' },
    }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).toHaveBeenCalledTimes(1)
    expect(toastError.mock.calls[0][1]).not.toMatch(/pymysql/i)
  })

  it('still shows 401 "sesion expirada" toast when offline (action required by user)', async () => {
    currentConnectivityOffline = true
    const handler = await getErrorHandler()
    const error = {
      response: { status: 401, data: { detail: 'expired' } },
      config: { url: '/api/produccion' },
    }
    await expect(handler(error)).rejects.toBe(error)
    expect(toastError).toHaveBeenCalledTimes(1)
    expect(toastError.mock.calls[0][0]).toBe('Sesion expirada')
  })
})
