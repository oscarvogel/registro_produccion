import db from '@/services/db'

const OFFLINE_SCHEMA_VERSION = 2

function createClientId() {
  return crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`
}

export async function queuePendingProductionRecord(payload) {
  return db.pendingRecords.add({
    payload,
    clientId: createClientId(),
    schemaVersion: OFFLINE_SCHEMA_VERSION,
    timestamp: Date.now(),
    synced: 0,
    syncStatus: 'pending',
    retryCount: 0,
  })
}
