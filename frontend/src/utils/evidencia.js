// Utilidades de la evidencia fotografica (issue #204).
//
// Son reglas de PRESENTACION (como se llama a cada rol y a cada estado), no
// de negocio: el backend es el que decide si la evidencia cubre el rol que
// el tipo de proceso exige.

export const ESTADO_PENDIENTE = 0
export const ESTADO_VERIFICADA = 1
export const ESTADO_RECHAZADA = 2
export const ESTADO_REEMPLAZADA = 3

export const ROL_PROCESADOR = 'procesador'
export const ROL_HOROMETRO = 'horometro'

/** Como se llama la foto segun el rol que cubre. */
export function rolLabel(tipo) {
  if (tipo === ROL_HOROMETRO) return 'Foto del horómetro'
  if (tipo === ROL_PROCESADOR) return 'Foto de la pantalla del procesador'
  return 'Foto de evidencia'
}

/** Estado de la foto, tal como lo ve el operador y el encargado. */
export function estadoLabel(estado) {
  const valor = Number(estado)
  if (valor === ESTADO_VERIFICADA) return 'Verificada'
  if (valor === ESTADO_RECHAZADA) return 'Rechazada'
  if (valor === ESTADO_REEMPLAZADA) return 'Reemplazada'
  return 'Pendiente de verificación'
}

/** Tono del AppBadge segun el estado de la foto. */
export function estadoTone(estado) {
  const valor = Number(estado)
  if (valor === ESTADO_VERIFICADA) return 'success'
  if (valor === ESTADO_RECHAZADA) return 'error'
  if (valor === ESTADO_REEMPLAZADA) return 'neutral'
  return 'warning'
}

/** Un registro queda OBSERVADO cuando una de sus fotos fue rechazada (D-C). */
export function esObservado(registro) {
  return Number(registro?.evidencias_rechazadas || 0) > 0
}

/** Un registro tiene fotos esperando la revision del encargado. */
export function tieneEvidenciaPendiente(registro) {
  return Number(registro?.evidencias_pendientes || 0) > 0
}

/** Opciones del filtro de evidencia del dashboard. */
export const FILTROS_EVIDENCIA = [
  { value: '', label: 'Todas' },
  { value: 'pendiente', label: 'Esperando verificación' },
  { value: 'rechazada', label: 'Con foto rechazada' },
  { value: 'sin_evidencia', label: 'Sin evidencia' },
]
