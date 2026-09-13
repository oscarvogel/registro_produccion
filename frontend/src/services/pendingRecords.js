import db from '@/services/db'

const OFFLINE_SCHEMA_VERSION = 3

export const SUBMISSION_KIND_FIELD = '__submission_kind'
export const SUBMISSION_KIND_PRODUCCION = 'produccion'
export const SUBMISSION_KIND_CAMINOS = 'caminos'
export const SUBMISSION_KIND_COMBUSTIBLE = 'combustible'

export function pendingSubmissionKind(payload = {}) {
  return payload?.[SUBMISSION_KIND_FIELD] || SUBMISSION_KIND_PRODUCCION
}

export function pendingSubmissionEndpoint(payload = {}) {
  const kind = pendingSubmissionKind(payload)
  if (kind === SUBMISSION_KIND_CAMINOS) return '/api/produccion/caminos'
  if (kind === SUBMISSION_KIND_COMBUSTIBLE) return '/api/combustible/cargas'
  return '/api/produccion/'
}

export function stripPendingMetadata(payload = {}) {
  const { [SUBMISSION_KIND_FIELD]: _kind, ...clean } = payload
  return clean
}

function createClientId() {
  return crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`
}

export async function queuePendingProductionRecord(payload) {
  const clientId = payload?.form_uuid || createClientId()
  return db.pendingRecords.add({
    payload,
    clientId,
    schemaVersion: OFFLINE_SCHEMA_VERSION,
    timestamp: Date.now(),
    synced: 0,
    syncStatus: 'pending',
    retryCount: 0,
  })
}

export async function ensurePendingIdentity(record) {
  const formUuid = record.payload?.form_uuid || record.clientId || createClientId()
  const payload = {
    ...record.payload,
    form_uuid: formUuid,
  }
  if (record.clientId !== formUuid || record.payload?.form_uuid !== formUuid) {
    await db.pendingRecords.update(record.id, { clientId: formUuid, payload })
  }
  return payload
}
