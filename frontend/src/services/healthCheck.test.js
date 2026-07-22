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
  it('returns "ok" when the probe returns a JSON array', async () => {
    let captured
    fakeFetchOnce(jsonResponse([{ id: 1 }], { status: 200 }))
    const result = await checkBackend({
      path: '/api/produccion/lugares-carga?un_id=1',
      onResult: (state, latency) => {
        captured = { state, latency }
      },
    })
    expect(result).toBe('ok')
    expect(captured.state).toBe('ok')
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/produccion/lugares-carga?un_id=1'),
      expect.objectContaining({ cache: 'no-store', credentials: 'omit' }),
    )
  })

  it('returns "ok" when the probe returns a JSON object with at least one key', async () => {
    fakeFetchOnce(jsonResponse({ status: 'ok', database: 'ok' }, { status: 200 }))
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('ok')
  })

  it('returns "degraded" when the probe returns 503', async () => {
    fakeFetchOnce(jsonResponse({ status: 'error', database: 'error' }, { status: 503 }))
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('degraded')
  })

  it('returns "degraded" when the body is an empty {} (no payload)', async () => {
    fakeFetchOnce(jsonResponse({}, { status: 200 }))
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('degraded')
  })

  it('returns "unreachable" when the response is 404 (probe path missing)', async () => {
    // /api/health is currently blocked by Nginx -> 404 -> unreachable, not degraded.
    fakeFetchOnce(jsonResponse({ detail: 'Not Found' }, { status: 404 }))
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('unreachable')
  })

  it('returns "unreachable" when fetch rejects with a network error', async () => {
    fakeFetchReject(new TypeError('Failed to fetch'))
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('unreachable')
  })

  it('returns "timeout" when the AbortController fires', async () => {
    globalThis.fetch = vi.fn((_url, init) => {
      return new Promise((_resolve, reject) => {
        init.signal.addEventListener('abort', () => {
          const e = new Error('aborted')
          e.name = 'AbortError'
          reject(e)
        })
      })
    })
    const start = Date.now()
    const result = await checkBackend({ path: '/api/health', timeoutMs: 50 })
    const elapsed = Date.now() - start
    expect(result).toBe('timeout')
    expect(elapsed).toBeGreaterThanOrEqual(40)
    expect(elapsed).toBeLessThan(500)
  })

  it('uses relative probe path when no baseURL is configured', async () => {
    globalThis.fetch = vi.fn(() =>
      Promise.resolve(jsonResponse([{ id: 1 }], { status: 200 })),
    )
    await checkBackend({ baseURL: '', path: '/api/health' })
    const [url] = globalThis.fetch.mock.calls[0]
    expect(url).toBe('/api/health')
  })

  it('honors an absolute probe URL when one is configured', async () => {
    globalThis.fetch = vi.fn(() =>
      Promise.resolve(jsonResponse([{ id: 1 }], { status: 200 })),
    )
    await checkBackend({
      baseURL: '/api/',
      path: 'https://other.example.com/health',
    })
    const [url] = globalThis.fetch.mock.calls[0]
    expect(url).toBe('https://other.example.com/health')
  })

  it('treats malformed JSON as degraded (no crash)', async () => {
    fakeFetchOnce({
      ok: true,
      status: 200,
      json: () => Promise.reject(new SyntaxError('bad json')),
    })
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('degraded')
  })

  it('never throws', async () => {
    fakeFetchReject(new Error('boom'))
    const result = await checkBackend({ path: '/api/health' })
    expect(result).toBe('unreachable')
  })

  it('runs a custom validator when provided', async () => {
    fakeFetchOnce(jsonResponse({ status: 'maintenance' }, { status: 200 }))
    const result = await checkBackend({
      path: '/api/health',
      validate: (data) => data && data.status === 'ok',
    })
    expect(result).toBe('degraded')
  })
})
