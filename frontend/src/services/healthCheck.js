/**
 * Tiny healthcheck that bypasses the global axios instance + interceptors so
 * the result never lights up a toast or triggers 401 cleanup. It uses fetch()
 * with an AbortController-based timeout.
 *
 * Returns one of:
 *   - 'ok'         backend reachable and reports healthy
 *   - 'degraded'   backend reachable but reports degraded (e.g. 503 with payload)
 *   - 'unreachable' request failed before reaching the server (network / DNS / CORS)
 *   - 'timeout'    request did not complete within `timeoutMs`
 *
 * Never throws. The connectivity store uses these values to flip isBackendUp
 * without firing toasts.
 *
 * @param {object} [opts]
 * @param {string} [opts.baseURL]  Override the API base URL. Defaults to VITE_API_URL.
 * @param {number} [opts.timeoutMs=3000]
 * @param {(state: string, latencyMs: number) => void} [opts.onResult] Optional callback
 */
export async function checkBackend({
  baseURL,
  timeoutMs = 3000,
  onResult,
} = {}) {
  const rawBase = baseURL ?? import.meta.env?.VITE_API_URL ?? ''
  // Strip a trailing `/api` segment so `/api` and `/api/` collapse to empty
  // (same convention as the axios client). Also drop the trailing slash.
  const base = rawBase.replace(/\/api\/?$/, '').replace(/\/$/, '')
  const url = `${base}/api/health`

  const ctrl = new AbortController()
  const started = Date.now()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)

  try {
    const res = await fetch(url, {
      signal: ctrl.signal,
      cache: 'no-store',
      headers: { Accept: 'application/json' },
      credentials: 'omit',
    })
    clearTimeout(timer)

    if (res.status >= 500) {
      onResult?.('degraded', Date.now() - started)
      return 'degraded'
    }

    const data = await res.json().catch(() => ({}))
    if (data && data.status === 'ok') {
      onResult?.('ok', Date.now() - started)
      return 'ok'
    }

    onResult?.('degraded', Date.now() - started)
    return 'degraded'
  } catch (err) {
    clearTimeout(timer)
    if (err && (err.name === 'AbortError' || err.code === 20)) {
      onResult?.('timeout', Date.now() - started)
      return 'timeout'
    }
    onResult?.('unreachable', Date.now() - started)
    return 'unreachable'
  }
}
