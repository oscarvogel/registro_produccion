export const ADMIN_PASSWORD_MAX_BYTES = 72
export const ADMIN_PASSWORD_TOO_LONG_MESSAGE = 'La contrasena es demasiado larga. Usa hasta 72 caracteres o una clave mas corta.'

export function passwordByteLength(password = '') {
  return new TextEncoder().encode(String(password)).length
}

export function validateAdminPassword(password) {
  if (!password) return ''
  if (passwordByteLength(password) > ADMIN_PASSWORD_MAX_BYTES) {
    return ADMIN_PASSWORD_TOO_LONG_MESSAGE
  }
  return ''
}
