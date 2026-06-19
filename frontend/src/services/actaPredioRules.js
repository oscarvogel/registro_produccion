const REQUIRED_PROCESS_NAMES = ['arauco']

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

export function shouldShowActaPredioFields(processType) {
  return processRequiresActaPredio(processType?.nombre || processType?.name || processType)
}

export function cleanActaPredioValues(form) {
  form.acta = ''
  form.predio_id = ''
  form.rodal_id = ''
  form.rodal_manual = ''
}
