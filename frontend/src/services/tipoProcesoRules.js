// Reglas de un tipo de proceso que no dependen de la ubicacion operativa.
//
// `requiere_horometro` llega desde el backend (tipo_de_proceso). Si el tipo
// de proceso no lo trae (por ejemplo datos cacheados antes de esta version),
// se asume `true` para conservar el comportamiento historico: el parte pide
// horometro inicial/final.

export function processRequiresHorometro(processType) {
  if (!processType || typeof processType !== 'object') return true
  if (!Object.prototype.hasOwnProperty.call(processType, 'requiere_horometro')) return true
  return Boolean(processType.requiere_horometro)
}

// ─── Evidencia fotografica (issue #200) ────────────────────────────
// El paso "Evidencia" aparece solo cuando el tipo de proceso exige foto.
// A diferencia del horometro (que viene del backend en `requiere_horometro`),
// los flags de evidencia son opcionales: sin datos NO se exige foto.
export const ROL_PROCESADOR = 'procesador'
export const ROL_HOROMETRO = 'horometro'

export function processRequiresEvidence(processType) {
  if (!processType || typeof processType !== 'object') return false
  return Boolean(processType.requiere_foto_procesador || processType.requiere_foto_horometro)
}

// Roles de evidencia que exige el tipo de proceso.
export function evidenceRoles(processType) {
  const roles = []
  if (!processType || typeof processType !== 'object') return roles
  if (processType.requiere_foto_procesador) roles.push(ROL_PROCESADOR)
  if (processType.requiere_foto_horometro) roles.push(ROL_HOROMETRO)
  return roles
}

// Pasos del wizard de carga de produccion.
export const PRODUCCION_STEPS = [
  { key: 'contexto', label: 'Contexto' },
  { key: 'operador', label: 'Operador' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'proceso', label: 'Proceso' },
  { key: 'tiempo', label: 'Tiempo' },
  { key: 'produccion', label: 'Producción' },
  { key: 'evidencia', label: 'Evidencia' },
  { key: 'consumos', label: 'Consumos' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'revision', label: 'Revisión' },
]

// El paso "Tiempo" (horometro inicial/final) solo aplica a procesos que
// requieren horometro. Una camioneta, por ejemplo, lo omite.
// El paso "Evidencia" solo aplica a los procesos que exigen foto.
export function productionSteps(processType) {
  const requires = processRequiresHorometro(processType)
  const evidence = processRequiresEvidence(processType)
  return PRODUCCION_STEPS.filter((step) => {
    if (step.key === 'tiempo') return requires
    if (step.key === 'evidencia') return evidence
    return true
  })
}
