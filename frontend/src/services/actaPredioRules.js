const REQUIRED_PROCESS_NAMES = ['arauco']
const LOCATION_FLAG_KEYS = ['requiere_acta', 'requiere_predio', 'requiere_rodal']

export function normalizeProcessName(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
}

export function processRequiresActaPredio(processName) {
  const normalized = normalizeProcessName(processName)
  if (!normalized) return false
  if (REQUIRED_PROCESS_NAMES.includes(normalized)) return true
  return normalized.includes('biomasa') && normalized.includes('gajos')
}

function hasBackendLocationFlags(processType) {
  if (!processType || typeof processType !== 'object') return false
  return LOCATION_FLAG_KEYS.some((key) => Object.prototype.hasOwnProperty.call(processType, key))
}

export function getLocationRequirements(processType) {
  if (hasBackendLocationFlags(processType)) {
    return {
      requiere_acta: Boolean(processType.requiere_acta),
      requiere_predio: Boolean(processType.requiere_predio),
      requiere_rodal: Boolean(processType.requiere_rodal),
    }
  }

  const fallbackRequired = processRequiresActaPredio(processType?.nombre || processType?.name || processType)
  return {
    requiere_acta: fallbackRequired,
    requiere_predio: fallbackRequired,
    requiere_rodal: fallbackRequired,
  }
}

export function shouldShowActaPredioFields(processType) {
  const requirements = getLocationRequirements(processType)
  return requirements.requiere_acta || requirements.requiere_predio || requirements.requiere_rodal
}

export function cleanLocationValues(form, requirements) {
  if (!requirements.requiere_acta) form.acta = ''
  if (!requirements.requiere_predio) form.predio_id = ''
  if (!requirements.requiere_rodal) {
    form.rodal_id = ''
    form.rodal_manual = ''
  }
}

export function cleanActaPredioValues(form) {
  cleanLocationValues(form, {
    requiere_acta: false,
    requiere_predio: false,
    requiere_rodal: false,
  })
}
