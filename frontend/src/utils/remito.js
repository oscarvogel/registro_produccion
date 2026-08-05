/**
 * Normalizacion canonica del numero de remito de combustible.
 *
 * Issue #124: el backend acepta "1" y "000000000001" como si fueran
 * remitos distintos, lo que hace que el reporte "Control de combustible"
 * muestre la misma carga dos veces.
 *
 * Esta utilidad refleja la logica del backend (`app/core/remito.py`) y se
 * usa desde los formularios para que el operador vea el formato canonico
 * apenas lo tipea, en vez de recibir el rechazo del backend en el submit.
 *
 * Reglas (identicas al backend):
 * - Solo letras A-Z, digitos 0-9 y guion.
 * - Si es puramente numerico: padding a 12 digitos con ceros a la izquierda.
 * - Si es alfanumerico (ej. "R-0001"): se mantiene, en mayusculas.
 * - Longitud maxima: 12 caracteres.
 *
 * Devuelve `null` si el valor no es normalizable (la UI debe mostrar
 * el valor que el operador escribio y dejar que el backend lo rechace
 * con un mensaje claro en lugar de mutarlo en silencio).
 */
const REMITO_MAX_LENGTH = 12
const ALLOWED_CHARS = /^[A-Z0-9-]+$/
const DIGITS_ONLY = /^[0-9]+$/

export function normalizeRemito(value) {
  if (value === null || value === undefined) return null
  const stripped = String(value).trim()
  if (!stripped) return ''

  const upper = stripped.toUpperCase()
  if (!ALLOWED_CHARS.test(upper)) return null

  if (DIGITS_ONLY.test(upper)) {
    if (upper.length > REMITO_MAX_LENGTH) return null
    return upper.padStart(REMITO_MAX_LENGTH, '0')
  }

  if (upper.length > REMITO_MAX_LENGTH) return null
  return upper
}

/**
 * Devuelve true si el valor ya esta en formato canonico.
 * Util para que el operador sepa que lo que ingreso es lo que se va a
 * guardar (y no algo distinto).
 */
export function isCanonicalRemito(value) {
  if (!value) return false
  const normalized = normalizeRemito(value)
  return normalized !== null && normalized === value
}
