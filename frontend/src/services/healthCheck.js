/**
 * Tiny healthcheck that bypasses the global axios instance + interceptors so
 * the result never lights up a toast or triggers 401 cleanup. It uses fetch()
 * with an AbortController-based timeout.
 *
 * Returns one of:
 *   - 'ok'         backend reachable and the probe succeeded
 *   - 'degraded'   backend reachable but the probe failed (5xx or malformed)
 *   - 'unreachable' request failed before reaching the server (network / DNS / CORS)
 *   - 'timeout'    request did not complete within `timeoutMs`
 *
 * Never throws. The connectivity store uses these values to flip isBackendUp
 * without firing toasts.
 *
 * Configuration via env (Vite):
 *   VITE_HEALTHCHECK_PATH  Default: "/api/produccion/lugares-carga?un_id=1"
 *
 * @param {object} [opts]
 * @param {string} [opts.baseURL]  Override the API base URL. Defaults to VITE_API_URL.
 * @param {string} [opts.path]     Override the probe path. Defaults to VITE_HEALTHCHECK_PATH.
 * @param {(raw: any) => boolean} [opts.validate] Optional validator on the parsed JSON
 *                                 body. Default: any non-empty array or object is ok.
 * @param {number} [opts.timeoutMs=3000]
 * @param {(state: string, latencyMs: number) => void} [opts.onResult] Optional callback
 */
export async function checkBackend({
  baseURL,
  path,
  validate,
  timeoutMs = 3000,
  onResult,
} = {}) {
  const rawBase = baseURL ?? import.meta.env?.VITE_API_URL ?? ''
  const rawPath =
    path ?? import.meta.env?.VITE_HEALTHCHECK_PATH ?? '/api/produccion/lugares-carga?un_id=1'

  // Normalize baseURL so a trailing /api collapses to empty (same convention
  // as the axios client). The path is taken as-is — it may already include
  // a host or query string.
  const base = rawBase.replace(/\/api\/?$/, '').replace(/\/$/, '')
  let url
  if (/^https?:\/\//i.test(rawPath)) {
    url = rawPath
  } else {
    const slash = base && !rawPath.startsWith('/') ? '/' : ''
    url = `${base}${slash}${rawPath}`
  }

  const ctrl = new AbortController()
  const started = Date.now()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)

  const defaultValidate = (data) => {
    if (Array.isArray(data)) return true
    if (data && typeof data === 'object') return Object.keys(data).length > 0
    return false
  }
  const isHealthyPayload = validate || defaultValidate

  try {
    const res = await fetch(url, {
      method: 'GET',
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
    if (res.status === 404) {
      // The probe path was removed from Nginx — treat as unreachable so the
      // banner shows the right colour, and avoid marking the backend down for
      // a missing route.
      onResult?.('unreachable', Date.now() - started)
      return 'unreachable'
    }

    let data
    try {
      data = await res.json()
    } catch {
      onResult?.('degraded', Date.now() - started)
      return 'degraded'
    }
    if (isHealthyPayload(data)) {
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
