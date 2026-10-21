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

// Pasos del wizard de carga de produccion.
export const PRODUCCION_STEPS = [
  { key: 'contexto', label: 'Contexto' },
  { key: 'operador', label: 'Operador' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'proceso', label: 'Proceso' },
  { key: 'tiempo', label: 'Tiempo' },
  { key: 'produccion', label: 'Producción' },
  { key: 'consumos', label: 'Consumos' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'revision', label: 'Revisión' },
]

// El paso "Tiempo" (horometro inicial/final) solo aplica a procesos que
// requieren horometro. Una camioneta, por ejemplo, lo omite.
export function productionSteps(processType) {
  const requires = processRequiresHorometro(processType)
  return PRODUCCION_STEPS.filter((step) => step.key !== 'tiempo' || requires)
}
