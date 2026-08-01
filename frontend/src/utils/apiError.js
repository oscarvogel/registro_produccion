/**
 * Helpers for surfacing backend errors to operators without leaking
 * Pydantic / FastAPI internals into the toasts.
 *
 * The backend now exposes a single `detail` string for validation failures
 * (and a `detail` string for HTTPException), but older / unhandled shapes
 * (raw arrays of Pydantic objects, error messages containing code paths,
 * etc.) still arrive from a few endpoints. These helpers normalise the
 * most common shapes so every caller in the app shows a single sentence
 * the operator can act on.
 */

const FALLBACK_MESSAGE =
  'No se pudo completar la operacion. Intenta nuevamente en unos minutos.'

const FALLBACK_VALIDATION_MESSAGE =
  'Los datos enviados no son validos. Revisa los campos del formulario e intenta nuevamente.'

const PYDANTIC_TYPE_MESSAGES = {
  int_parsing: 'uno de los campos numericos no es un numero valido',
  float_parsing: 'uno de los campos numericos no es un numero valido',
  missing: 'faltan datos obligatorios del formulario',
  string_too_long: 'uno de los textos excede el tamano maximo permitido',
  string_type: 'uno de los campos esperaba texto',
  greater_than_equal: 'uno de los campos numericos es menor al minimo permitido',
  greater_than: 'uno de los campos numericos debe ser mayor a cero',
  json_invalid: 'el cuerpo de la solicitud no tiene un formato valido',
}

const VALUE_ERROR_PREFIX = 'Value error, '

/**
 * Build a user-friendly string from a Pydantic `value_error` raised by a
 * custom model validator. Pydantic 2.x wraps the original `ValueError`
 * message as `"Value error, <message>"` — strip that prefix so the toast
 * shows the actual sentence we wrote on the backend.
 */
function humanizeValueError(message) {
  const trimmed = String(message || '').trim()
  if (!trimmed) return ''
  if (trimmed.startsWith(VALUE_ERROR_PREFIX)) {
    return trimmed.slice(VALUE_ERROR_PREFIX.length)
  }
  return trimmed
}

function humanizePydanticError(entry) {
  if (!entry || typeof entry !== 'object') return ''
  if (entry.type === 'value_error') {
    return humanizeValueError(entry.msg)
  }
  const mapped = PYDANTIC_TYPE_MESSAGES[entry.type]
  if (mapped) return mapped
  return ''
}

function humanizePydanticArray(detail) {
  if (!Array.isArray(detail) || detail.length === 0) return ''
  for (const entry of detail) {
    const message = humanizePydanticError(entry)
    if (message) return message
  }
  return ''
}

/**
 * Extract a single user-friendly string from any axios / fetch error.
 *
 * - If the backend already returned a string `detail` (the new global
 *   validation handler does this), it is returned as-is.
 * - If `detail` is a Pydantic-style array of error objects, the first
 *   humanised message is returned.
 * - Anything that does not match a known shape falls back to a generic
 *   Spanish sentence so the operator never sees a raw JSON dump.
 *
 * @param {unknown} error Anything axios / fetch rejected with.
 * @param {string} [fallback] Optional override for the generic fallback.
 * @returns {string}
 */
export function extractApiErrorMessage(error, fallback = FALLBACK_MESSAGE) {
  if (!error) return fallback

  // Network / aborted requests land here with no `response`.
  if (typeof error === 'object' && error && !error.response) {
    return fallback
  }

  const data = error?.response?.data
  if (data && typeof data === 'object') {
    const detail = data.detail

    if (typeof detail === 'string' && detail.trim()) {
      return detail.trim()
    }

    if (Array.isArray(detail)) {
      const message = humanizePydanticArray(detail)
      if (message) return message
    }
  }

  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message.trim()
  }

  return fallback
}

/**
 * Specialised helper for HTTP 422 (validation) responses. The backend's
 * new global handler already returns a string, but if a legacy endpoint
 * still returns a Pydantic array we still want a clean message.
 */
export function extractValidationErrorMessage(
  error,
  fallback = FALLBACK_VALIDATION_MESSAGE,
) {
  const message = extractApiErrorMessage(error, fallback)
  if (message && message !== FALLBACK_MESSAGE) return message
  if (error?.response?.status === 422) return fallback
  return message
}

/**
 * Defence-in-depth: some of our form inputs use `v-model.number` on
 * cleared fields, which produces `""` (or `null`) in the payload.
 * The backend now coerces those to `0`, but normalising client-side
 * avoids a round-trip and keeps the offline queue clean.
 *
 * The list mirrors `_NUMERIC_FIELDS` in `backend/app/schemas/produccion.py`.
 * Keep them in sync.
 */
const NUMERIC_FIELDS = new Set([
  'cod_operador',
  'cod_equipo',
  'hr_inicio',
  'hr_fin',
  'combustible',
  'km_combustible',
  'aceite_cadena',
  'aceite_hidraulico',
  'aceite_motor',
  'aceite_transmision',
  'aceite_embrague',
  'm3',
  'carros',
  'tn_despachadas',
  'has',
  'produccion',
  'plantas',
  'mtrs_recorridos',
  'km_carreteo',
  'km_perfilado',
  'hr_disposicion',
  'hrs_no_op',
  'espada',
  'puntera',
  'cadena',
  'pinon',
  'cantidad_cadenas',
  'pies_16',
  'pies_14',
  'pies_12',
  'pies_10',
  'pulpable',
  'lugar_carga',
  'codigo_tabla',
  'id_tipo_comb',
])

/**
 * Return a shallow copy of `payload` where known numeric fields with
 * `""` or `null` (typical of cleared `<input type="number">` values)
 * are replaced with `0`. Non-numeric fields are left untouched.
 */
export function normalizeProduccionPayload(payload) {
  if (!payload || typeof payload !== 'object') return payload
  const normalised = { ...payload }
  for (const field of NUMERIC_FIELDS) {
    if (!(field in normalised)) continue
    const value = normalised[field]
    if (value === null || (typeof value === 'string' && value.trim() === '')) {
      normalised[field] = 0
    }
  }
  return normalised
}
