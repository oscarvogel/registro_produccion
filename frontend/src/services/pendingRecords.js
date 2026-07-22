import db from '@/services/db'

const OFFLINE_SCHEMA_VERSION = 2

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
