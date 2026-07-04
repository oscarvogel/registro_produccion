import { afterEach, describe, expect, it, vi } from 'vitest'
import { checkBackend } from './healthCheck'

const originalFetch = globalThis.fetch

afterEach(() => {
  globalThis.fetch = originalFetch
  vi.restoreAllMocks()
})

function fakeFetchOnce(response) {
  globalThis.fetch = vi.fn(() => Promise.resolve(response))
}

function fakeFetchReject(error) {
  globalThis.fetch = vi.fn(() => Promise.reject(error))
}

function jsonResponse(body, { status = 200 } = {}) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  }
}

describe('checkBackend', () => {
  it('returns "ok" when the backend responds 200 with status=ok', async () => {
    let captured
    fakeFetchOnce(jsonResponse({ status: 'ok', database: 'ok' }, { status: 200 }))
    const result = await checkBackend({
      baseURL: 'http://api.example.com',
      onResult: (state, latency) => {
        captured = { state, latency }
      },
    })
    expect(result).toBe('ok')
    expect(captured.state).toBe('ok')
    expect(globalThis.fetch).toHaveBeenCalledWith(
      'http://api.example.com/api/health',
      expect.objectContaining({ cache: 'no-store', credentials: 'omit' }),
    )
  })

  it('returns "degraded" when the backend responds 503 (unhealthy but reachable)', async () => {
    fakeFetchOnce(jsonResponse({ status: 'error', database: 'error' }, { status: 503 }))
    const result = await checkBackend({ baseURL: 'http://api.example.com' })
    expect(result).toBe('degraded')
  })

  it('returns "degraded" when 200 payload has status=error', async () => {
    fakeFetchOnce(jsonResponse({ status: 'error', database: 'ok' }, { status: 200 }))
    const result = await checkBackend({ baseURL: 'http://api.example.com' })
    expect(result).toBe('degraded')
  })

  it('returns "unreachable" when fetch rejects with a network error', async () => {
    fakeFetchReject(new TypeError('Failed to fetch'))
    const result = await checkBackend({ baseURL: 'http://api.example.com' })
    expect(result).toBe('unreachable')
  })

  it('returns "timeout" when the AbortController fires', async () => {
    let abortHandler
    globalThis.fetch = vi.fn((_url, init) => {
      abortHandler = init.signal
      return new Promise((_resolve, reject) => {
        init.signal.addEventListener('abort', () => {
          const e = new Error('aborted')
          e.name = 'AbortError'
          reject(e)
        })
      })
    })
    const start = Date.now()
    const result = await checkBackend({
      baseURL: 'http://api.example.com',
      timeoutMs: 50,
    })
    const elapsed = Date.now() - start
    expect(result).toBe('timeout')
    expect(elapsed).toBeGreaterThanOrEqual(40)
    expect(elapsed).toBeLessThan(500)
    expect(abortHandler.aborted).toBe(true)
  })

  it('uses relative /api/health when no baseURL is configured', async () => {
    globalThis.fetch = vi.fn(() => Promise.resolve(jsonResponse({ status: 'ok' }, { status: 200 })))
    await checkBackend({ baseURL: '' })
    const [url] = globalThis.fetch.mock.calls[0]
    expect(url).toBe('/api/health')
  })

  it('uses /api baseURL normalized to relative', async () => {
    globalThis.fetch = vi.fn(() => Promise.resolve(jsonResponse({ status: 'ok' }, { status: 200 })))
    await checkBackend({ baseURL: '/api/' })
    const [url] = globalThis.fetch.mock.calls[0]
    expect(url).toBe('/api/health')
  })

  it('strips trailing slash from baseURL', async () => {
    globalThis.fetch = vi.fn(() => Promise.resolve(jsonResponse({ status: 'ok' }, { status: 200 })))
    await checkBackend({ baseURL: 'http://api.example.com/' })
    const [url] = globalThis.fetch.mock.calls[0]
    expect(url).toBe('http://api.example.com/api/health')
  })

  it('treats malformed JSON as degraded (no crash)', async () => {
    fakeFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.reject(new SyntaxError('bad json')),
    })
    const result = await checkBackend({ baseURL: 'http://api.example.com' })
    expect(result).toBe('degraded')
  })

  it('never throws', async () => {
    fakeFetchReject(new Error('boom'))
    const result = await checkBackend({ baseURL: 'http://api.example.com' })
    expect(result).toBe('unreachable')
  })
})
