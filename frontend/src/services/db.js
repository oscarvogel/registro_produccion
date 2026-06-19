import Dexie from 'dexie'

const db = new Dexie('produccion_offline')

db.version(1).stores({
  // ++id = auto-increment primary key
  // payload = the full form data object to POST to the server
  // timestamp = when it was created offline (ms since epoch)
  // synced = 0 pending, 1 synced (we delete after sync, but flag helps debugging)
  pendingRecords: '++id, timestamp, synced',
})

db.version(2).stores({
  pendingRecords: '++id, timestamp, synced, syncStatus, clientId',
})

db.version(3).stores({
  pendingRecords: '++id, timestamp, synced, syncStatus, clientId',
  catalogos: 'key, catalog, timestamp',
})

export default db
